import pytest
from datetime import date, timedelta

from apps.study_plan.models import ActiveLearningNote, GuidedReflection, LessonProgress, StudyChapter, StudyModule
from apps.study_plan.services.plan_service import PlanService


@pytest.fixture
def module(db):
    return StudyModule.objects.create(
        title="Módulo Teste",
        slug="modulo-teste",
        order=1,
        master_file="test.md",
        category="specific",
        study_phase="1",
        estimated_hours=4.0,
    )


@pytest.fixture
def chapter(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Teste",
        slug="capitulo-teste",
        order=1,
        estimated_minutes=30,
    )


@pytest.fixture
def chapter2(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Dois",
        slug="capitulo-dois",
        order=2,
        estimated_minutes=25,
    )


@pytest.mark.django_db
def test_module_progress_zero_when_no_activity(user, module, chapter):
    mp = PlanService.get_module_progress(user, module)
    assert mp.total_chapters == 1
    assert mp.completed == 0
    assert mp.percentage == 0.0


@pytest.mark.django_db
def test_module_progress_updates_when_completed(user, module, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    mp = PlanService.get_module_progress(user, module)
    assert mp.completed == 1
    assert mp.percentage == 100.0


@pytest.mark.django_db
def test_mark_chapter_started_creates_in_progress(user, chapter):
    progress = PlanService.mark_chapter_started(user, chapter)
    assert progress.status == LessonProgress.IN_PROGRESS
    assert progress.started_at is not None


@pytest.mark.django_db
def test_mark_chapter_completed_sets_completed_at(user, chapter):
    progress = PlanService.mark_chapter_completed(user, chapter)
    assert progress.status == LessonProgress.COMPLETED
    assert progress.completed_at is not None


@pytest.mark.django_db
def test_mark_chapter_completed_idempotent(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    PlanService.mark_chapter_completed(user, chapter)
    assert LessonProgress.objects.filter(user=user, chapter=chapter).count() == 1


@pytest.mark.django_db
def test_get_next_chapter_returns_first_when_no_progress(user, module, chapter, chapter2):
    next_ch = PlanService.get_next_chapter(user)
    assert next_ch.id == chapter.id


@pytest.mark.django_db
def test_get_next_chapter_skips_completed(user, module, chapter, chapter2):
    PlanService.mark_chapter_completed(user, chapter)
    next_ch = PlanService.get_next_chapter(user)
    assert next_ch.id == chapter2.id


@pytest.mark.django_db
def test_get_next_chapter_returns_none_when_all_done(user, module, chapter, chapter2):
    PlanService.mark_chapter_completed(user, chapter)
    PlanService.mark_chapter_completed(user, chapter2)
    assert PlanService.get_next_chapter(user) is None


@pytest.mark.django_db
def test_plan_streak_zero_when_no_activity(user):
    assert PlanService.get_plan_streak(user) == 0


@pytest.mark.django_db
def test_plan_streak_counts_consecutive_days(user, chapter):
    progress = PlanService.mark_chapter_completed(user, chapter)
    assert PlanService.get_plan_streak(user) >= 1


# ── Fase 2: ActiveLearningNote ───────────────────────────────────────────

@pytest.mark.django_db
def test_save_active_note_creates(user, chapter):
    note = PlanService.save_active_note(user, chapter, "Explico o conteúdo com minhas palavras aqui.")
    assert ActiveLearningNote.objects.filter(user=user, chapter=chapter).count() == 1
    assert note.explanation == "Explico o conteúdo com minhas palavras aqui."


@pytest.mark.django_db
def test_save_active_note_updates_on_second_call(user, chapter):
    PlanService.save_active_note(user, chapter, "Primeira versão da explicação aqui.")
    PlanService.save_active_note(user, chapter, "Segunda versão atualizada da explicação.")
    assert ActiveLearningNote.objects.filter(user=user, chapter=chapter).count() == 1
    note = ActiveLearningNote.objects.get(user=user, chapter=chapter)
    assert "Segunda" in note.explanation


# ── Fase 2: GuidedReflection ─────────────────────────────────────────────

@pytest.mark.django_db
def test_save_guided_reflection_creates(user, chapter):
    reflection = PlanService.save_guided_reflection(
        user, chapter,
        what_understood="Entendi o conceito principal do tema.",
        most_important="A parte mais importante foi a definição central.",
        most_difficult="Tive dificuldade com os detalhes técnicos específicos.",
    )
    assert GuidedReflection.objects.filter(user=user, chapter=chapter).count() == 1
    assert reflection.what_understood == "Entendi o conceito principal do tema."


@pytest.mark.django_db
def test_save_guided_reflection_updates_on_second_call(user, chapter):
    PlanService.save_guided_reflection(user, chapter, "v1 entendido", "v1 importante", "v1 difícil")
    PlanService.save_guided_reflection(user, chapter, "v2 entendido", "v2 importante", "v2 difícil")
    assert GuidedReflection.objects.filter(user=user, chapter=chapter).count() == 1
    r = GuidedReflection.objects.get(user=user, chapter=chapter)
    assert r.what_understood == "v2 entendido"


# ── Fase 2: ChapterCompletionStatus ──────────────────────────────────────

@pytest.mark.django_db
def test_chapter_completion_status_all_false(user, chapter):
    status = PlanService.get_chapter_completion_status(user, chapter)
    assert not status.is_reading_done
    assert not status.has_note
    assert not status.has_reflection
    assert not status.is_fully_done


@pytest.mark.django_db
def test_chapter_completion_status_reading_done(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    status = PlanService.get_chapter_completion_status(user, chapter)
    assert status.is_reading_done
    assert not status.has_note
    assert not status.is_fully_done


@pytest.mark.django_db
def test_chapter_completion_status_fully_done(user, chapter):
    PlanService.mark_chapter_completed(user, chapter)
    PlanService.save_active_note(user, chapter, "Explicação completa do conteúdo aprendido aqui.")
    PlanService.save_guided_reflection(user, chapter, "Entendido", "Importante", "Difícil")
    status = PlanService.get_chapter_completion_status(user, chapter)
    assert status.is_fully_done
