import pytest
from datetime import date, timedelta
from unittest.mock import patch

from apps.exams.models import Quiz, QuizQuestion, UserAnswer
from apps.questions.models import Alternative, Question, Subject
from apps.study_plan.models import ErrorNotebookEntry, _next_review_date
from apps.study_plan.services.error_notebook_service import ErrorNotebookService


@pytest.fixture
def subject(db):
    return Subject.objects.create(name="Zoonoses", slug="zoonoses-nb", is_active=True)


@pytest.fixture
def question(db, subject):
    q = Question.objects.create(
        subject=subject,
        text="Questão de teste para caderno",
        external_id="nb-q-001",
        is_active=True,
    )
    Alternative.objects.create(question=q, letter="A", text="Certa", is_correct=True)
    Alternative.objects.create(question=q, letter="B", text="Errada", is_correct=False)
    Alternative.objects.create(question=q, letter="C", text="Errada", is_correct=False)
    Alternative.objects.create(question=q, letter="D", text="Errada", is_correct=False)
    return q


@pytest.fixture
def question2(db, subject):
    q = Question.objects.create(
        subject=subject,
        text="Segunda questão",
        external_id="nb-q-002",
        is_active=True,
    )
    Alternative.objects.create(question=q, letter="A", text="Certa", is_correct=True)
    Alternative.objects.create(question=q, letter="B", text="Errada", is_correct=False)
    Alternative.objects.create(question=q, letter="C", text="Errada", is_correct=False)
    Alternative.objects.create(question=q, letter="D", text="Errada", is_correct=False)
    return q


@pytest.fixture
def quiz_com_erros(db, user, question, question2):
    quiz = Quiz.objects.create(
        user=user,
        quiz_type=Quiz.PRACTICE,
        status=Quiz.FINISHED,
        quantity=2,
    )
    QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
    QuizQuestion.objects.create(quiz=quiz, question=question2, order=2)

    alt_errada = question.alternatives.filter(is_correct=False).first()
    alt_errada2 = question2.alternatives.filter(is_correct=False).first()

    UserAnswer.objects.create(
        quiz=quiz, question=question,
        selected_alternative=alt_errada, is_correct=False
    )
    UserAnswer.objects.create(
        quiz=quiz, question=question2,
        selected_alternative=alt_errada2, is_correct=False
    )
    return quiz


@pytest.fixture
def quiz_com_pulada(db, user, question):
    quiz = Quiz.objects.create(
        user=user,
        quiz_type=Quiz.PRACTICE,
        status=Quiz.FINISHED,
        quantity=1,
    )
    QuizQuestion.objects.create(quiz=quiz, question=question, order=1)
    UserAnswer.objects.create(
        quiz=quiz, question=question,
        selected_alternative=None, is_correct=False
    )
    return quiz


@pytest.mark.django_db
def test_sync_errors_cria_entradas(user, quiz_com_erros):
    synced = ErrorNotebookService.sync_errors(user, quiz_com_erros)
    assert synced == 2
    assert ErrorNotebookEntry.objects.filter(user=user).count() == 2


@pytest.mark.django_db
def test_sync_errors_incrementa_wrong_count(user, question, quiz_com_erros):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    entry = ErrorNotebookEntry.objects.get(user=user, question=question)
    assert entry.wrong_count == 1

    # Novo quiz com o mesmo erro
    quiz2 = Quiz.objects.create(user=user, quiz_type=Quiz.PRACTICE, status=Quiz.FINISHED, quantity=1)
    QuizQuestion.objects.create(quiz=quiz2, question=question, order=1)
    alt_errada = question.alternatives.filter(is_correct=False).first()
    UserAnswer.objects.create(quiz=quiz2, question=question, selected_alternative=alt_errada, is_correct=False)

    ErrorNotebookService.sync_errors(user, quiz2)
    entry.refresh_from_db()
    assert entry.wrong_count == 2


@pytest.mark.django_db
def test_sync_errors_puladas_nao_vao_para_caderno(user, quiz_com_pulada):
    synced = ErrorNotebookService.sync_errors(user, quiz_com_pulada)
    assert synced == 0
    assert ErrorNotebookEntry.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_sync_errors_idempotente(user, quiz_com_erros):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    # O wrong_count deve ser 2 porque rodou duas vezes com o mesmo quiz
    entry = ErrorNotebookEntry.objects.filter(user=user).first()
    assert entry is not None
    # Idempotência no sentido de que não duplica entradas (unique_together)
    assert ErrorNotebookEntry.objects.filter(user=user).count() == 2


@pytest.mark.django_db
def test_next_review_at_logica():
    today = date.today()
    assert _next_review_date(1) == today + timedelta(days=1)
    assert _next_review_date(2) == today + timedelta(days=3)
    assert _next_review_date(3) == today + timedelta(days=7)
    assert _next_review_date(4) == today + timedelta(days=14)
    assert _next_review_date(10) == today + timedelta(days=14)


@pytest.mark.django_db
def test_mark_as_reviewed(user, quiz_com_erros, question):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    entry = ErrorNotebookEntry.objects.get(user=user, question=question)
    result = ErrorNotebookService.mark_as_reviewed(user, str(entry.id))
    assert result.is_reviewed is True
    assert result.next_review_at is None


@pytest.mark.django_db
def test_save_personal_note(user, quiz_com_erros, question):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    entry = ErrorNotebookEntry.objects.get(user=user, question=question)
    ErrorNotebookService.save_personal_note(user, str(entry.id), "Minha anotação")
    entry.refresh_from_db()
    assert entry.personal_note == "Minha anotação"


@pytest.mark.django_db
def test_get_notebook_retorna_entries(user, quiz_com_erros):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    qs = ErrorNotebookService.get_notebook(user)
    assert qs.count() == 2


@pytest.mark.django_db
def test_get_notebook_filtra_por_is_reviewed(user, quiz_com_erros, question):
    ErrorNotebookService.sync_errors(user, quiz_com_erros)
    entry = ErrorNotebookEntry.objects.get(user=user, question=question)
    ErrorNotebookService.mark_as_reviewed(user, str(entry.id))

    pendentes = ErrorNotebookService.get_notebook(user, is_reviewed=False)
    revisadas = ErrorNotebookService.get_notebook(user, is_reviewed=True)
    assert pendentes.count() == 1
    assert revisadas.count() == 1
