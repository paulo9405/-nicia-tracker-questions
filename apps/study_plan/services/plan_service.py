from __future__ import annotations

import calendar as cal_module
from dataclasses import dataclass, field
from datetime import date, timedelta

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.study_plan.models import (
    ActiveLearningNote,
    ErrorNotebookEntry,
    GuidedReflection,
    LessonProgress,
    StudyChapter,
    StudyModule,
)


@dataclass
class ProgressStats:
    total_modules: int
    completed_modules: int
    total_chapters: int
    completed_chapters: int
    in_progress_chapters: int
    overall_percentage: float
    notes_created: int
    reflections_created: int
    mini_quizzes_done: int
    errors_pending: int
    errors_reviewed: int
    current_streak: int
    max_streak: int
    total_study_days: int
    total_minutes_estimated: int


@dataclass
class ChapterCompletionStatus:
    is_reading_done: bool
    has_note: bool
    has_reflection: bool

    @property
    def is_fully_done(self) -> bool:
        return self.is_reading_done and self.has_note and self.has_reflection


@dataclass
class ModuleProgress:
    module: StudyModule
    total_chapters: int
    completed: int
    in_progress: int
    percentage: float = field(init=False)

    def __post_init__(self):
        self.percentage = round(self.completed / self.total_chapters * 100, 1) if self.total_chapters else 0.0


@dataclass
class PlanSummary:
    total_modules: int
    total_chapters: int
    completed_chapters: int
    in_progress_chapters: int
    overall_percentage: float
    streak_days: int
    module_progresses: list[ModuleProgress]
    next_chapter: StudyChapter | None


class PlanService:

    @staticmethod
    def get_module_progress(user, module: StudyModule) -> ModuleProgress:
        chapters = module.chapters.filter(is_active=True)
        total = chapters.count()
        if total == 0:
            return ModuleProgress(module=module, total_chapters=0, completed=0, in_progress=0)

        chapter_ids = list(chapters.values_list("id", flat=True))
        progresses = LessonProgress.objects.filter(
            user=user, chapter_id__in=chapter_ids
        )
        completed = progresses.filter(status=LessonProgress.COMPLETED).count()
        in_progress = progresses.filter(status=LessonProgress.IN_PROGRESS).count()

        return ModuleProgress(
            module=module,
            total_chapters=total,
            completed=completed,
            in_progress=in_progress,
        )

    @staticmethod
    def get_plan_summary(user) -> PlanSummary:
        modules = StudyModule.objects.filter(is_active=True).select_related("subject")
        module_progresses = []
        total_chapters = 0
        total_completed = 0
        total_in_progress = 0

        for module in modules:
            mp = PlanService.get_module_progress(user, module)
            module_progresses.append(mp)
            total_chapters += mp.total_chapters
            total_completed += mp.completed
            total_in_progress += mp.in_progress

        overall_pct = round(total_completed / total_chapters * 100, 1) if total_chapters else 0.0
        streak = PlanService.get_plan_streak(user)
        next_chapter = PlanService.get_next_chapter(user)

        return PlanSummary(
            total_modules=modules.count(),
            total_chapters=total_chapters,
            completed_chapters=total_completed,
            in_progress_chapters=total_in_progress,
            overall_percentage=overall_pct,
            streak_days=streak,
            module_progresses=module_progresses,
            next_chapter=next_chapter,
        )

    @staticmethod
    def get_next_chapter(user) -> StudyChapter | None:
        """Retorna o próximo capítulo a ser estudado: em andamento primeiro, depois não iniciado."""
        # Primeiro: capítulo em andamento mais antigo
        in_progress = (
            LessonProgress.objects.filter(user=user, status=LessonProgress.IN_PROGRESS)
            .select_related("chapter__module")
            .order_by("chapter__module__order", "chapter__order")
            .first()
        )
        if in_progress:
            return in_progress.chapter

        # Segundo: próximo capítulo não iniciado (por ordem de módulo e capítulo)
        completed_ids = LessonProgress.objects.filter(
            user=user, status=LessonProgress.COMPLETED
        ).values_list("chapter_id", flat=True)

        in_progress_ids = LessonProgress.objects.filter(
            user=user, status=LessonProgress.IN_PROGRESS
        ).values_list("chapter_id", flat=True)

        excluded = list(completed_ids) + list(in_progress_ids)

        return (
            StudyChapter.objects.filter(is_active=True)
            .exclude(id__in=excluded)
            .select_related("module")
            .order_by("module__order", "order")
            .first()
        )

    @staticmethod
    def get_all_activity_dates(user) -> set:
        """União de todas as datas com qualquer atividade relevante no Plano de Estudos."""
        from apps.exams.models import Quiz

        dates: set = set()
        dates.update(
            LessonProgress.objects.filter(user=user, status=LessonProgress.COMPLETED)
            .exclude(completed_at__isnull=True)
            .values_list("completed_at__date", flat=True)
        )
        dates.update(
            ActiveLearningNote.objects.filter(user=user)
            .values_list("created_at__date", flat=True)
        )
        dates.update(
            GuidedReflection.objects.filter(user=user)
            .values_list("created_at__date", flat=True)
        )
        dates.update(
            Quiz.objects.filter(user=user, quiz_type=Quiz.MINI, status=Quiz.FINISHED)
            .exclude(finished_at__isnull=True)
            .values_list("finished_at__date", flat=True)
        )
        return dates

    @staticmethod
    def get_plan_streak(user) -> int:
        """Dias consecutivos com pelo menos 1 atividade relevante no Plano de Estudos."""
        activity_dates = PlanService.get_all_activity_dates(user)
        if not activity_dates:
            return 0

        today = date.today()
        streak = 0
        current = today

        while current in activity_dates:
            streak += 1
            current -= timedelta(days=1)

        if streak == 0:
            current = today - timedelta(days=1)
            while current in activity_dates:
                streak += 1
                current -= timedelta(days=1)

        return streak

    @staticmethod
    def get_max_streak(user) -> int:
        """Maior sequência consecutiva de dias com atividade já registrada."""
        all_dates = sorted(PlanService.get_all_activity_dates(user))
        if not all_dates:
            return 0
        max_s = 1
        current_s = 1
        for i in range(1, len(all_dates)):
            if all_dates[i] - all_dates[i - 1] == timedelta(days=1):
                current_s += 1
                if current_s > max_s:
                    max_s = current_s
            else:
                current_s = 1
        return max_s

    @staticmethod
    def get_total_study_days(user) -> int:
        """Total de dias distintos com atividade."""
        return len(PlanService.get_all_activity_dates(user))

    @staticmethod
    def get_calendar_weeks(user, year: int, month: int) -> list:
        """Grade do calendário mensal: lista de semanas, cada semana é lista de (day, active)."""
        activity_dates = PlanService.get_all_activity_dates(user)
        month_active = {d for d in activity_dates if d.year == year and d.month == month}

        c = cal_module.Calendar(firstweekday=0)
        weeks_raw = c.monthdayscalendar(year, month)
        result = []
        for week in weeks_raw:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append((0, False))
                else:
                    d = date(year, month, day)
                    week_data.append((day, d in month_active))
            result.append(week_data)
        return result

    @staticmethod
    def get_progress_stats(user) -> ProgressStats:
        """Agrega todas as métricas de progresso para a ProgressView."""
        from apps.exams.models import Quiz

        modules = StudyModule.objects.filter(is_active=True)
        total_modules = modules.count()

        all_chapter_ids = list(
            StudyChapter.objects.filter(is_active=True).values_list("id", flat=True)
        )
        total_chapters = len(all_chapter_ids)

        completed_progresses = LessonProgress.objects.filter(
            user=user, status=LessonProgress.COMPLETED
        )
        completed_chapter_ids = set(completed_progresses.values_list("chapter_id", flat=True))
        completed_chapters = len(completed_chapter_ids)

        in_progress_chapters = LessonProgress.objects.filter(
            user=user, status=LessonProgress.IN_PROGRESS
        ).count()

        overall_pct = round(completed_chapters / total_chapters * 100, 1) if total_chapters else 0.0

        # Módulos 100% concluídos: todos os capítulos ativos do módulo estão concluídos
        completed_modules = 0
        for module in modules:
            chapter_ids_in_module = set(
                module.chapters.filter(is_active=True).values_list("id", flat=True)
            )
            if chapter_ids_in_module and chapter_ids_in_module.issubset(completed_chapter_ids):
                completed_modules += 1

        notes_created = ActiveLearningNote.objects.filter(user=user).count()
        reflections_created = GuidedReflection.objects.filter(user=user).count()

        mini_quizzes_done = Quiz.objects.filter(
            user=user, quiz_type=Quiz.MINI, status=Quiz.FINISHED
        ).count()

        errors_pending = ErrorNotebookEntry.objects.filter(user=user, is_reviewed=False).count()
        errors_reviewed = ErrorNotebookEntry.objects.filter(user=user, is_reviewed=True).count()

        current_streak = PlanService.get_plan_streak(user)
        max_streak = PlanService.get_max_streak(user)
        total_study_days = PlanService.get_total_study_days(user)

        # Minutos estimados dos capítulos concluídos
        completed_chapter_qs = StudyChapter.objects.filter(
            id__in=completed_chapter_ids, is_active=True
        )
        minutes_agg = completed_chapter_qs.aggregate(total=Sum("estimated_minutes"))
        total_minutes = minutes_agg["total"] or 0

        return ProgressStats(
            total_modules=total_modules,
            completed_modules=completed_modules,
            total_chapters=total_chapters,
            completed_chapters=completed_chapters,
            in_progress_chapters=in_progress_chapters,
            overall_percentage=overall_pct,
            notes_created=notes_created,
            reflections_created=reflections_created,
            mini_quizzes_done=mini_quizzes_done,
            errors_pending=errors_pending,
            errors_reviewed=errors_reviewed,
            current_streak=current_streak,
            max_streak=max_streak,
            total_study_days=total_study_days,
            total_minutes_estimated=total_minutes,
        )

    @staticmethod
    def mark_chapter_started(user, chapter: StudyChapter) -> LessonProgress:
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={"status": LessonProgress.IN_PROGRESS, "started_at": timezone.now()},
        )
        if not created and progress.status == LessonProgress.NOT_STARTED:
            progress.status = LessonProgress.IN_PROGRESS
            progress.started_at = timezone.now()
            progress.save(update_fields=["status", "started_at", "updated_at"])
        return progress

    @staticmethod
    def mark_chapter_completed(user, chapter: StudyChapter) -> LessonProgress:
        progress, _ = LessonProgress.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={
                "status": LessonProgress.COMPLETED,
                "started_at": timezone.now(),
                "completed_at": timezone.now(),
            },
        )
        if progress.status != LessonProgress.COMPLETED:
            progress.status = LessonProgress.COMPLETED
            progress.completed_at = timezone.now()
            if not progress.started_at:
                progress.started_at = timezone.now()
            progress.save(update_fields=["status", "completed_at", "started_at", "updated_at"])
        return progress

    @staticmethod
    def get_chapter_completion_status(user, chapter: StudyChapter) -> ChapterCompletionStatus:
        progress = LessonProgress.objects.filter(user=user, chapter=chapter).first()
        is_reading_done = bool(progress and progress.status == LessonProgress.COMPLETED)
        has_note = ActiveLearningNote.objects.filter(user=user, chapter=chapter).exists()
        has_reflection = GuidedReflection.objects.filter(user=user, chapter=chapter).exists()
        return ChapterCompletionStatus(
            is_reading_done=is_reading_done,
            has_note=has_note,
            has_reflection=has_reflection,
        )

    @staticmethod
    @transaction.atomic
    def save_active_note(user, chapter: StudyChapter, explanation: str) -> ActiveLearningNote:
        note, _ = ActiveLearningNote.objects.update_or_create(
            user=user,
            chapter=chapter,
            defaults={"explanation": explanation},
        )
        return note

    @staticmethod
    @transaction.atomic
    def save_guided_reflection(
        user,
        chapter: StudyChapter,
        what_understood: str,
        most_important: str,
        most_difficult: str,
    ) -> GuidedReflection:
        reflection, _ = GuidedReflection.objects.update_or_create(
            user=user,
            chapter=chapter,
            defaults={
                "what_understood": what_understood,
                "most_important": most_important,
                "most_difficult": most_difficult,
            },
        )
        return reflection

    @staticmethod
    def get_calendar_activity(user, year: int, month: int) -> dict[date, int]:
        """Retorna dict {data: quantidade_capitulos_concluidos} para o mês."""
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        start = date(year, month, 1)
        end = date(year, month, last_day)

        rows = (
            LessonProgress.objects.filter(
                user=user,
                status=LessonProgress.COMPLETED,
                completed_at__date__range=(start, end),
            )
            .values("completed_at__date")
            .annotate(count=Count("id"))
        )
        return {row["completed_at__date"]: row["count"] for row in rows}
