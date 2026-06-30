import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, TemplateView, View

from apps.questions.models import Subject

from .forms import ActiveLearningNoteForm, GuidedReflectionForm
from .models import ActiveLearningNote, ErrorNotebookEntry, GuidedReflection, LessonProgress, StudyChapter, StudyModule
from .services.error_notebook_service import ErrorNotebookService
from .services.mini_quiz_service import MiniQuizService
from .services.plan_service import PlanService


class PlanDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "study_plan/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["summary"] = PlanService.get_plan_summary(self.request.user)
        return ctx


class ModuleListView(LoginRequiredMixin, TemplateView):
    template_name = "study_plan/module_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        modules = StudyModule.objects.filter(is_active=True).select_related("subject")
        progresses = [
            PlanService.get_module_progress(self.request.user, m)
            for m in modules
        ]
        ctx["specific_progresses"] = [p for p in progresses if p.module.category == "specific"]
        ctx["basic_progresses"] = [p for p in progresses if p.module.category == "basic"]
        return ctx


class ModuleDetailView(LoginRequiredMixin, TemplateView):
    template_name = "study_plan/module_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        module = get_object_or_404(StudyModule, slug=kwargs["slug"], is_active=True)
        chapters = module.chapters.filter(is_active=True)

        user = self.request.user
        progress_map = {
            p.chapter_id: p
            for p in LessonProgress.objects.filter(user=user, chapter__in=chapters)
        }
        chapters_with_progress = [
            (ch, progress_map.get(ch.id)) for ch in chapters
        ]

        ctx["module"] = module
        ctx["module_progress"] = PlanService.get_module_progress(user, module)
        ctx["chapters_with_progress"] = chapters_with_progress
        return ctx


class ChapterReadView(LoginRequiredMixin, TemplateView):
    template_name = "study_plan/chapter_read.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chapter = get_object_or_404(
            StudyChapter,
            slug=kwargs["slug"],
            module__slug=kwargs["module_slug"],
            is_active=True,
        )
        user = self.request.user

        PlanService.mark_chapter_started(user, chapter)
        progress, _ = LessonProgress.objects.get_or_create(
            user=user,
            chapter=chapter,
            defaults={"status": LessonProgress.IN_PROGRESS, "started_at": timezone.now()},
        )

        # Capítulo anterior e próximo dentro do módulo
        module = chapter.module
        chapters_qs = list(module.chapters.filter(is_active=True).order_by("order"))
        idx = next((i for i, c in enumerate(chapters_qs) if c.id == chapter.id), None)
        prev_chapter = chapters_qs[idx - 1] if idx and idx > 0 else None
        next_chapter = chapters_qs[idx + 1] if idx is not None and idx + 1 < len(chapters_qs) else None

        ctx["chapter"] = chapter
        ctx["module"] = module
        ctx["progress"] = progress
        ctx["prev_chapter"] = prev_chapter
        ctx["next_chapter"] = next_chapter
        return ctx


class ChapterCompleteView(LoginRequiredMixin, View):
    """POST: marca capítulo como concluído e redireciona para aprendizagem ativa."""

    def post(self, request, module_slug, slug):
        chapter = get_object_or_404(StudyChapter, slug=slug, module__slug=module_slug, is_active=True)
        PlanService.mark_chapter_completed(request.user, chapter)
        messages.success(request, f'Capítulo "{chapter.title}" concluído! Agora registre o que aprendeu.')
        return redirect("study_plan:chapter_note", module_slug=module_slug, slug=chapter.slug)


class ChapterNoteView(LoginRequiredMixin, FormView):
    """GET/POST: aprendizagem ativa — explicação livre do conteúdo."""

    template_name = "study_plan/chapter_note.html"
    form_class = ActiveLearningNoteForm

    def _get_chapter(self):
        return get_object_or_404(
            StudyChapter,
            slug=self.kwargs["slug"],
            module__slug=self.kwargs["module_slug"],
            is_active=True,
        )

    def get_initial(self):
        note = ActiveLearningNote.objects.filter(
            user=self.request.user, chapter=self._get_chapter()
        ).first()
        if note:
            return {"explanation": note.explanation}
        return {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chapter = self._get_chapter()
        ctx["chapter"] = chapter
        ctx["module"] = chapter.module
        ctx["existing_note"] = ActiveLearningNote.objects.filter(
            user=self.request.user, chapter=chapter
        ).first()
        ctx["completion_status"] = PlanService.get_chapter_completion_status(
            self.request.user, chapter
        )
        return ctx

    def form_valid(self, form):
        chapter = self._get_chapter()
        PlanService.save_active_note(
            user=self.request.user,
            chapter=chapter,
            explanation=form.cleaned_data["explanation"],
        )
        messages.success(self.request, "Nota salva! Agora responda às perguntas de reflexão.")
        return redirect("study_plan:chapter_reflection", module_slug=self.kwargs["module_slug"], slug=chapter.slug)


class ChapterReflectionView(LoginRequiredMixin, FormView):
    """GET/POST: reflexão guiada — 3 perguntas sobre o capítulo."""

    template_name = "study_plan/chapter_reflection.html"
    form_class = GuidedReflectionForm

    def _get_chapter(self):
        return get_object_or_404(
            StudyChapter,
            slug=self.kwargs["slug"],
            module__slug=self.kwargs["module_slug"],
            is_active=True,
        )

    def get_initial(self):
        reflection = GuidedReflection.objects.filter(
            user=self.request.user, chapter=self._get_chapter()
        ).first()
        if reflection:
            return {
                "what_understood": reflection.what_understood,
                "most_important": reflection.most_important,
                "most_difficult": reflection.most_difficult,
            }
        return {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chapter = self._get_chapter()
        ctx["chapter"] = chapter
        ctx["module"] = chapter.module
        ctx["existing_reflection"] = GuidedReflection.objects.filter(
            user=self.request.user, chapter=chapter
        ).first()
        ctx["completion_status"] = PlanService.get_chapter_completion_status(
            self.request.user, chapter
        )
        return ctx

    def form_valid(self, form):
        chapter = self._get_chapter()
        PlanService.save_guided_reflection(
            user=self.request.user,
            chapter=chapter,
            what_understood=form.cleaned_data["what_understood"],
            most_important=form.cleaned_data["most_important"],
            most_difficult=form.cleaned_data["most_difficult"],
        )
        messages.success(
            self.request,
            "Reflexão salva! Agora pratique com questões do banco.",
        )
        return redirect("study_plan:chapter_mini_quiz", module_slug=self.kwargs["module_slug"], slug=chapter.slug)


class ChapterMiniQuizView(LoginRequiredMixin, TemplateView):
    """GET: exibe tela do mini quiz com informações. POST: cria o quiz e redireciona."""

    template_name = "study_plan/chapter_mini_quiz.html"

    def _get_chapter(self):
        return get_object_or_404(
            StudyChapter,
            slug=self.kwargs["slug"],
            module__slug=self.kwargs["module_slug"],
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chapter = self._get_chapter()
        questions = MiniQuizService.get_questions_for_chapter(chapter)
        has_enough = len(questions) >= 3

        ctx["chapter"] = chapter
        ctx["module"] = chapter.module
        ctx["available_count"] = len(questions)
        ctx["has_enough_questions"] = has_enough
        ctx["suggested_questions"] = questions if has_enough else []
        ctx["completion_status"] = PlanService.get_chapter_completion_status(
            self.request.user, chapter
        )
        return ctx

    def post(self, request, module_slug, slug):
        chapter = self._get_chapter()
        quiz = MiniQuizService.create_mini_quiz(request.user, chapter)
        if quiz is None:
            messages.warning(
                request,
                "Não há questões suficientes no banco para este tema. Continue treinando!",
            )
            return redirect("study_plan:chapter_mini_quiz", module_slug=module_slug, slug=slug)
        return redirect("exams:play", pk=quiz.pk)


class ErrorNotebookView(LoginRequiredMixin, TemplateView):
    """Lista paginada do caderno de erros."""

    template_name = "study_plan/error_notebook.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        subject_id = self.request.GET.get("subject", "")
        is_reviewed_param = self.request.GET.get("is_reviewed", "")
        order_by = self.request.GET.get("order", "-wrong_count")

        is_reviewed = None
        if is_reviewed_param == "0":
            is_reviewed = False
        elif is_reviewed_param == "1":
            is_reviewed = True

        entries_qs = ErrorNotebookService.get_notebook(
            user,
            subject_id=subject_id or None,
            is_reviewed=is_reviewed,
            order_by=order_by,
        )

        paginator = Paginator(entries_qs, 20)
        page = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page)

        ctx["page_obj"] = page_obj
        ctx["subjects"] = Subject.objects.filter(is_active=True).order_by("name")
        ctx["total_count"] = ErrorNotebookEntry.objects.filter(user=user).count()
        ctx["pending_count"] = ErrorNotebookEntry.objects.filter(user=user, is_reviewed=False).count()
        ctx["filter_subject_id"] = subject_id
        ctx["filter_is_reviewed"] = is_reviewed_param
        ctx["filter_order"] = order_by
        return ctx


class ErrorNoteView(LoginRequiredMixin, View):
    """POST: salva anotação pessoal em uma entrada do caderno."""

    def post(self, request, pk):
        note = request.POST.get("personal_note", "")
        try:
            ErrorNotebookService.save_personal_note(request.user, pk, note)
            messages.success(request, "Anotação salva.")
        except ErrorNotebookEntry.DoesNotExist:
            raise Http404
        return redirect("study_plan:error_notebook")


class ErrorReviewView(LoginRequiredMixin, View):
    """POST: marca uma entrada do caderno como revisada."""

    def post(self, request, pk):
        try:
            ErrorNotebookService.mark_as_reviewed(request.user, pk)
            messages.success(request, "Questão marcada como revisada.")
        except ErrorNotebookEntry.DoesNotExist:
            raise Http404
        return redirect("study_plan:error_notebook")


_MONTH_NAMES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


class ProgressView(LoginRequiredMixin, TemplateView):
    """Página de progresso detalhado: métricas, streak e calendário de atividade."""

    template_name = "study_plan/progress.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()

        try:
            year = int(self.request.GET.get("year", today.year))
            month = int(self.request.GET.get("month", today.month))
            if not (1 <= month <= 12):
                year, month = today.year, today.month
        except (ValueError, TypeError):
            year, month = today.year, today.month

        ctx["stats"] = PlanService.get_progress_stats(user)
        ctx["calendar_weeks"] = PlanService.get_calendar_weeks(user, year, month)
        ctx["calendar_year"] = year
        ctx["calendar_month"] = month
        ctx["calendar_month_name"] = _MONTH_NAMES_PT[month]
        ctx["today"] = today

        if month == 1:
            ctx["prev_year"], ctx["prev_month"] = year - 1, 12
        else:
            ctx["prev_year"], ctx["prev_month"] = year, month - 1

        if month == 12:
            ctx["next_year"], ctx["next_month"] = year + 1, 1
        else:
            ctx["next_year"], ctx["next_month"] = year, month + 1

        return ctx
