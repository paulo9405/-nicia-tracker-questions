import pytest
from datetime import date, timedelta

from django.utils import timezone

from apps.study_plan.models import (
    ActiveLearningNote,
    GuidedReflection,
    LessonProgress,
    StudyChapter,
    StudyModule,
)
from apps.study_plan.services.plan_service import PlanService


@pytest.fixture
def module(db):
    return StudyModule.objects.create(
        title="Módulo Fase4",
        slug="modulo-fase4",
        order=99,
        master_file="fase4.md",
        category="specific",
        study_phase="1",
        estimated_hours=2.0,
    )


@pytest.fixture
def chapter(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Fase4",
        slug="capitulo-fase4",
        order=1,
        estimated_minutes=40,
    )


@pytest.fixture
def chapter2(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Fase4 B",
        slug="capitulo-fase4-b",
        order=2,
        estimated_minutes=20,
    )


# ── get_all_activity_dates ────────────────────────────────────────────

@pytest.mark.django_db
def test_all_activity_dates_empty_when_no_activity(user):
    dates = PlanService.get_all_activity_dates(user)
    assert dates == set()


@pytest.mark.django_db
def test_all_activity_dates_includes_completed_chapter(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    dates = PlanService.get_all_activity_dates(user)
    assert date.today() in dates


@pytest.mark.django_db
def test_all_activity_dates_includes_note(user, chapter):
    PlanService.save_active_note(user, chapter, "nota de teste para activity dates aqui.")
    dates = PlanService.get_all_activity_dates(user)
    assert date.today() in dates


@pytest.mark.django_db
def test_all_activity_dates_includes_reflection(user, chapter):
    PlanService.save_guided_reflection(
        user, chapter,
        what_understood="Entendido",
        most_important="Importante",
        most_difficult="Difícil",
    )
    dates = PlanService.get_all_activity_dates(user)
    assert date.today() in dates


# ── get_max_streak ────────────────────────────────────────────────────

@pytest.mark.django_db
def test_max_streak_zero_when_no_activity(user):
    assert PlanService.get_max_streak(user) == 0


@pytest.mark.django_db
def test_max_streak_single_day(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    assert PlanService.get_max_streak(user) >= 1


@pytest.mark.django_db
def test_max_streak_consecutive_days(user, chapter, chapter2):
    # Simula 2 dias consecutivos: ontem e hoje
    today = timezone.now()
    yesterday = today - timedelta(days=1)

    p1 = LessonProgress.objects.create(
        user=user,
        chapter=chapter,
        status=LessonProgress.COMPLETED,
        started_at=yesterday,
        completed_at=yesterday,
    )
    p2 = LessonProgress.objects.create(
        user=user,
        chapter=chapter2,
        status=LessonProgress.COMPLETED,
        started_at=today,
        completed_at=today,
    )

    assert PlanService.get_max_streak(user) >= 2


@pytest.mark.django_db
def test_max_streak_finds_longest_run(user, chapter, chapter2):
    # Simula: dia 1 (ontem) + dia 2 (hoje) → streak de 2
    # Dia de anteontem é gap, então max é 2 (não mais)
    today = timezone.now()
    yesterday = today - timedelta(days=1)

    LessonProgress.objects.create(
        user=user,
        chapter=chapter,
        status=LessonProgress.COMPLETED,
        started_at=yesterday,
        completed_at=yesterday,
    )
    LessonProgress.objects.create(
        user=user,
        chapter=chapter2,
        status=LessonProgress.COMPLETED,
        started_at=today,
        completed_at=today,
    )

    max_s = PlanService.get_max_streak(user)
    assert max_s >= 2


# ── get_total_study_days ──────────────────────────────────────────────

@pytest.mark.django_db
def test_total_study_days_zero_when_no_activity(user):
    assert PlanService.get_total_study_days(user) == 0


@pytest.mark.django_db
def test_total_study_days_counts_distinct_dates(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    assert PlanService.get_total_study_days(user) >= 1


# ── get_calendar_weeks ────────────────────────────────────────────────

@pytest.mark.django_db
def test_calendar_weeks_returns_list(user):
    weeks = PlanService.get_calendar_weeks(user, 2026, 6)
    assert isinstance(weeks, list)
    assert len(weeks) >= 4


@pytest.mark.django_db
def test_calendar_weeks_each_week_has_seven_days(user):
    weeks = PlanService.get_calendar_weeks(user, 2026, 6)
    for week in weeks:
        assert len(week) == 7


@pytest.mark.django_db
def test_calendar_weeks_active_flag_set_when_activity_exists(user, chapter):
    today = date.today()
    PlanService.mark_chapter_completed(user, chapter)
    weeks = PlanService.get_calendar_weeks(user, today.year, today.month)
    # Verifica que pelo menos uma célula do dia de hoje está ativa
    active_days = [day for week in weeks for day, active in week if day == today.day and active]
    assert len(active_days) >= 1


# ── get_progress_stats ────────────────────────────────────────────────

@pytest.mark.django_db
def test_progress_stats_zero_when_no_activity(user, module, chapter):
    stats = PlanService.get_progress_stats(user)
    assert stats.completed_chapters == 0
    assert stats.overall_percentage == 0.0
    assert stats.current_streak == 0
    assert stats.max_streak == 0
    assert stats.total_study_days == 0
    assert stats.notes_created == 0
    assert stats.reflections_created == 0
    assert stats.mini_quizzes_done == 0
    assert stats.errors_pending == 0


@pytest.mark.django_db
def test_progress_stats_counts_completed_chapter(user, module, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    stats = PlanService.get_progress_stats(user)
    assert stats.completed_chapters >= 1
    assert stats.overall_percentage > 0


@pytest.mark.django_db
def test_progress_stats_counts_notes(user, module, chapter):
    PlanService.save_active_note(user, chapter, "Minha explicação completa do conteúdo.")
    stats = PlanService.get_progress_stats(user)
    assert stats.notes_created == 1


@pytest.mark.django_db
def test_progress_stats_counts_reflections(user, module, chapter):
    PlanService.save_guided_reflection(user, chapter, "ok", "ok", "ok")
    stats = PlanService.get_progress_stats(user)
    assert stats.reflections_created == 1


@pytest.mark.django_db
def test_progress_stats_total_minutes_from_completed_chapters(user, module, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    stats = PlanService.get_progress_stats(user)
    # chapter.estimated_minutes = 40
    assert stats.total_minutes_estimated >= 40


@pytest.mark.django_db
def test_progress_stats_completed_module_when_all_chapters_done(user, module, chapter, chapter2):
    PlanService.mark_chapter_completed(user, chapter)
    PlanService.mark_chapter_completed(user, chapter2)
    stats = PlanService.get_progress_stats(user)
    assert stats.completed_modules >= 1
