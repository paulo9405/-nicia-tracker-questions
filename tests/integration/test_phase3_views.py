import pytest
from django.urls import reverse

from apps.exams.models import Quiz, QuizQuestion, UserAnswer
from apps.questions.models import Alternative, Question, Subject, Topic
from apps.study_plan.models import ErrorNotebookEntry, StudyChapter, StudyModule
from apps.study_plan.services.error_notebook_service import ErrorNotebookService


@pytest.fixture
def subject(db):
    return Subject.objects.create(name="Zoonoses", slug="zoo-phase3", is_active=True)


@pytest.fixture
def topic(db, subject):
    return Topic.objects.create(name="Raiva", slug="raiva-phase3", subject=subject, is_active=True)


@pytest.fixture
def questions(db, subject, topic):
    qs = []
    for i in range(5):
        q = Question.objects.create(
            subject=subject,
            topic=topic,
            text=f"Questão phase3 {i + 1}",
            external_id=f"phase3-q-{i + 1}",
            is_active=True,
        )
        for j, letter in enumerate("ABCD"):
            Alternative.objects.create(
                question=q, letter=letter,
                text=f"Alternativa {letter}",
                is_correct=(j == 0),
            )
        qs.append(q)
    return qs


@pytest.fixture
def module(db, subject):
    m = StudyModule.objects.create(
        title="Zoonoses Fase3",
        slug="zoonoses-fase3",
        order=50,
        master_file="test.md",
        category="specific",
        study_phase="1",
        estimated_hours=4.0,
    )
    m.subject = subject
    m.save()
    return m


@pytest.fixture
def chapter(db, module, subject):
    ch = StudyChapter.objects.create(
        module=module,
        title="Raiva Fase3",
        slug="raiva-fase3",
        order=1,
        estimated_minutes=30,
        tags=["raiva"],
    )
    ch.related_subjects.add(subject)
    return ch


@pytest.fixture
def chapter_sem_questoes(db, module):
    return StudyChapter.objects.create(
        module=module,
        title="Capítulo Sem Questões",
        slug="sem-questoes-fase3",
        order=99,
        tags=["tema-inexistente-xyz"],
    )


# ────────────────────────────────────────────────────────────────────────────
# ChapterMiniQuizView
# ────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_mini_quiz_requires_login(client, chapter):
    url = reverse("study_plan:chapter_mini_quiz", kwargs={"module_slug": chapter.module.slug, "slug": chapter.slug})
    r = client.get(url)
    assert r.status_code == 302
    assert "/conta/login/" in r.url


@pytest.mark.django_db
def test_mini_quiz_get_com_questoes(client_logged, chapter, questions):
    url = reverse("study_plan:chapter_mini_quiz", kwargs={"module_slug": chapter.module.slug, "slug": chapter.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "Iniciar Mini Quiz" in r.content.decode()


@pytest.mark.django_db
def test_mini_quiz_get_sem_questoes(client_logged, chapter_sem_questoes):
    url = reverse("study_plan:chapter_mini_quiz", kwargs={"module_slug": chapter_sem_questoes.module.slug, "slug": chapter_sem_questoes.slug})
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "insuficientes" in r.content.decode()


@pytest.mark.django_db
def test_mini_quiz_post_cria_quiz_e_redireciona(client_logged, chapter, questions):
    url = reverse("study_plan:chapter_mini_quiz", kwargs={"module_slug": module.slug, "slug": chapter.slug})
    r = client_logged.post(url)
    assert r.status_code == 302
    assert "/questoes/treino/" in r.url

    quiz = Quiz.objects.filter(quiz_type=Quiz.MINI, chapter=chapter).first()
    assert quiz is not None
    assert quiz.status == Quiz.IN_PROGRESS


@pytest.mark.django_db
def test_mini_quiz_post_sem_questoes_redireciona_de_volta(client_logged, chapter_sem_questoes):
    url = reverse("study_plan:chapter_mini_quiz", kwargs={"module_slug": chapter_sem_questoes.module.slug, "slug": chapter_sem_questoes.slug})
    r = client_logged.post(url)
    assert r.status_code == 302
    assert "mini-quiz" in r.url


# ────────────────────────────────────────────────────────────────────────────
# ErrorNotebookView
# ────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_error_notebook_requires_login(client):
    url = reverse("study_plan:error_notebook")
    r = client.get(url)
    assert r.status_code == 302
    assert "/conta/login/" in r.url


@pytest.mark.django_db
def test_error_notebook_get_vazio(client_logged):
    url = reverse("study_plan:error_notebook")
    r = client_logged.get(url)
    assert r.status_code == 200
    assert "Caderno de Erros" in r.content.decode()


@pytest.mark.django_db
def test_error_notebook_get_com_entradas(client_logged, user, subject, questions):
    question = questions[0]
    quiz = Quiz.objects.create(
        user=user, quiz_type=Quiz.PRACTICE, status=Quiz.FINISHED, quantity=1
    )
    QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
    alt_errada = question.alternatives.filter(is_correct=False).first()
    UserAnswer.objects.create(
        quiz=quiz, question=question, selected_alternative=alt_errada, is_correct=False
    )
    ErrorNotebookService.sync_errors(user, quiz)

    url = reverse("study_plan:error_notebook")
    r = client_logged.get(url)
    assert r.status_code == 200
    content = r.content.decode()
    assert "Zoonoses" in content
    assert "1 erro" in content


@pytest.mark.django_db
def test_error_notebook_filtro_disciplina(client_logged, user, subject, questions):
    question = questions[0]
    quiz = Quiz.objects.create(
        user=user, quiz_type=Quiz.PRACTICE, status=Quiz.FINISHED, quantity=1
    )
    QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
    alt_errada = question.alternatives.filter(is_correct=False).first()
    UserAnswer.objects.create(
        quiz=quiz, question=question, selected_alternative=alt_errada, is_correct=False
    )
    ErrorNotebookService.sync_errors(user, quiz)

    url = reverse("study_plan:error_notebook")
    r = client_logged.get(url, {"subject": str(subject.id)})
    assert r.status_code == 200
    assert "Zoonoses" in r.content.decode()


# ────────────────────────────────────────────────────────────────────────────
# ErrorNoteView / ErrorReviewView
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def notebook_entry(db, user, subject, questions):
    question = questions[0]
    quiz = Quiz.objects.create(
        user=user, quiz_type=Quiz.PRACTICE, status=Quiz.FINISHED, quantity=1
    )
    QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
    alt_errada = question.alternatives.filter(is_correct=False).first()
    ua = UserAnswer.objects.create(
        quiz=quiz, question=question, selected_alternative=alt_errada, is_correct=False
    )
    ErrorNotebookService.sync_errors(user, quiz)
    return ErrorNotebookEntry.objects.get(user=user, question=question)


@pytest.mark.django_db
def test_error_note_salva_anotacao(client_logged, notebook_entry):
    url = reverse("study_plan:error_note", kwargs={"pk": notebook_entry.id})
    r = client_logged.post(url, {"personal_note": "Devo revisar mais sobre este tema"})
    assert r.status_code == 302
    notebook_entry.refresh_from_db()
    assert notebook_entry.personal_note == "Devo revisar mais sobre este tema"


@pytest.mark.django_db
def test_error_review_marca_revisada(client_logged, notebook_entry):
    url = reverse("study_plan:error_review", kwargs={"pk": notebook_entry.id})
    r = client_logged.post(url)
    assert r.status_code == 302
    notebook_entry.refresh_from_db()
    assert notebook_entry.is_reviewed is True


# ────────────────────────────────────────────────────────────────────────────
# Hook em QuizService.submit_answers
# ────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_submit_answers_popula_caderno_automaticamente(user, subject, questions):
    """Após submit_answers, erros já estão no caderno."""
    from apps.exams.services.quiz_service import QuizService

    quiz = Quiz.objects.create(
        user=user, quiz_type=Quiz.PRACTICE, status=Quiz.IN_PROGRESS, quantity=2
    )
    q1, q2 = questions[0], questions[1]
    QuizQuestion.objects.create(quiz=quiz, question=q1, order=1)
    QuizQuestion.objects.create(quiz=quiz, question=q2, order=2)

    alt_errada_q1 = q1.alternatives.filter(is_correct=False).first()
    alt_certa_q2 = q2.alternatives.filter(is_correct=True).first()

    raw_answers = {
        str(q1.id): str(alt_errada_q1.id),
        str(q2.id): str(alt_certa_q2.id),
    }

    QuizService.submit_answers(quiz, raw_answers)

    # q1 errada → deve estar no caderno
    assert ErrorNotebookEntry.objects.filter(user=user, question=q1).exists()
    # q2 correta → não deve estar
    assert not ErrorNotebookEntry.objects.filter(user=user, question=q2).exists()
