import pytest
from django.urls import reverse

from apps.study_plan.models import ActiveLearningNote, GuidedReflection, LessonProgress, StudyChapter, StudyModule
from apps.study_plan.services.plan_service import PlanService


@pytest.fixture
def module(db):
    return StudyModule.objects.create(
        title="Saúde Única",
        slug="saude-unica-test",
        order=1,
        master_file="01_SAUDE_UNICA_MASTER.md",
        category="specific",
        study_phase="1",
        estimated_hours=8.0,
        icon="🌿",
    )


@pytest.fixture
def chapter(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="One Health",
        slug="one-health",
        order=1,
        estimated_minutes=40,
        tags=["one-health", "saude-unica"],
    )


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    url = reverse("study_plan:dashboard")
    r = client.get(url)
    assert r.status_code == 302
    assert "/conta/login/" in r.url


@pytest.mark.django_db
def test_dashboard_loads(client_logged, module, chapter):
    url = reverse("study_plan:dashboard")
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "Plano de Estudos" in r.content.decode()


@pytest.mark.django_db
def test_module_list_loads(client_logged, module):
    url = reverse("study_plan:module_list")
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "Saúde Única" in r.content.decode()


@pytest.mark.django_db
def test_module_detail_loads(client_logged, module, chapter):
    url = reverse("study_plan:module_detail", kwargs={"slug": module.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "One Health" in r.content.decode()


@pytest.mark.django_db
def test_chapter_read_creates_progress(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_read", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert LessonProgress.objects.filter(user=user, chapter=chapter).exists()


@pytest.mark.django_db
def test_chapter_complete_marks_completed(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_complete", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url)
    assert r.status_code == 302
    progress = LessonProgress.objects.get(user=user, chapter=chapter)
    assert progress.status == LessonProgress.COMPLETED


@pytest.mark.django_db
def test_chapter_complete_is_idempotent(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_complete", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    client_logged.post(url)
    client_logged.post(url)
    assert LessonProgress.objects.filter(user=user, chapter=chapter).count() == 1


@pytest.mark.django_db
def test_module_detail_404_for_unknown_slug(client_logged):
    url = reverse("study_plan:module_detail", kwargs={"slug": "nao-existe"})
    r = client_logged.get(url)
    assert r.status_code == 404


@pytest.mark.django_db
def test_chapter_read_404_for_unknown_slug(client_logged):
    url = reverse("study_plan:chapter_read", kwargs={"module_slug": "modulo-nao-existe", "slug": "nao-existe"})
    r = client_logged.get(url)
    assert r.status_code == 404


@pytest.mark.django_db
def test_chapter_complete_redirects_to_note(client_logged, module, chapter):
    url = reverse("study_plan:chapter_complete", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url)
    assert r.status_code == 302
    assert "nota" in r.url


# ── Fase 2: ChapterNoteView ──────────────────────────────────────────────

@pytest.mark.django_db
def test_chapter_note_requires_login(client, module, chapter):
    url = reverse("study_plan:chapter_note", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client.get(url)
    assert r.status_code == 302
    assert "/conta/login/" in r.url


@pytest.mark.django_db
def test_chapter_note_get_loads(client_logged, module, chapter):
    url = reverse("study_plan:chapter_note", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "explanation" in r.content.decode()


@pytest.mark.django_db
def test_chapter_note_post_creates_note(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_note", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url, {"explanation": "Esta é minha explicação com mais de vinte caracteres."})
    assert r.status_code == 302
    assert "reflexao" in r.url
    assert ActiveLearningNote.objects.filter(user=user, chapter=chapter).exists()


@pytest.mark.django_db
def test_chapter_note_post_rejects_short_explanation(client_logged, module, chapter):
    url = reverse("study_plan:chapter_note", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url, {"explanation": "Curto"})
    assert r.status_code == 200
    assert "20 caracteres" in r.content.decode()


@pytest.mark.django_db
def test_chapter_note_post_updates_existing_note(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_note", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    client_logged.post(url, {"explanation": "Primeira explicação com texto suficiente para validar."})
    client_logged.post(url, {"explanation": "Segunda explicação atualizada com texto suficiente também."})
    assert ActiveLearningNote.objects.filter(user=user, chapter=chapter).count() == 1
    note = ActiveLearningNote.objects.get(user=user, chapter=chapter)
    assert "Segunda" in note.explanation


# ── Fase 2: ChapterReflectionView ───────────────────────────────────────

@pytest.mark.django_db
def test_chapter_reflection_requires_login(client, module, chapter):
    url = reverse("study_plan:chapter_reflection", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client.get(url)
    assert r.status_code == 302
    assert "/conta/login/" in r.url


@pytest.mark.django_db
def test_chapter_reflection_get_loads(client_logged, module, chapter):
    url = reverse("study_plan:chapter_reflection", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "what_understood" in r.content.decode()


@pytest.mark.django_db
def test_chapter_reflection_post_creates_reflection(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_reflection", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url, {
        "what_understood": "Entendi o conceito principal.",
        "most_important": "A parte mais importante foi a definição.",
        "most_difficult": "Tive dificuldade com os detalhes técnicos.",
    })
    assert r.status_code == 302
    assert "capitulo" in r.url
    assert GuidedReflection.objects.filter(user=user, chapter=chapter).exists()


@pytest.mark.django_db
def test_chapter_reflection_post_updates_existing(client_logged, user, module, chapter):
    url = reverse("study_plan:chapter_reflection", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    data = {
        "what_understood": "Entendi o conceito.",
        "most_important": "A parte mais importante.",
        "most_difficult": "A parte mais difícil.",
    }
    client_logged.post(url, data)
    data["what_understood"] = "Versão atualizada do entendimento."
    client_logged.post(url, data)
    assert GuidedReflection.objects.filter(user=user, chapter=chapter).count() == 1
    r = GuidedReflection.objects.get(user=user, chapter=chapter)
    assert "atualizada" in r.what_understood
