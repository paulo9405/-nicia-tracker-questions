"""
Testes unitários do QuizService e QuestionService.
"""

import pytest

pytestmark = pytest.mark.django_db


# ── fixtures ────────────────────────────────────────────────────────────── #


@pytest.fixture
def subject(db):
    from apps.questions.models import Subject

    return Subject.objects.create(
        name="Saúde Única",
        slug="saude-unica",
        category="specific",
        color="#2e7d32",
    )


@pytest.fixture
def questions(subject):
    from apps.questions.models import Alternative, Question

    qs = []
    for i in range(15):
        q = Question.objects.create(
            subject=subject,
            external_id=f"test-s01-q{i+1:03d}",
            text=f"Enunciado da questão {i + 1}?",
        )
        for letter, correct in zip("ABCD", [False, False, False, True]):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
            )
        qs.append(q)
    return qs


# ── QuestionService ──────────────────────────────────────────────────────── #


class TestQuestionService:
    def test_retorna_questoes_ativas(self, questions, subject):
        from apps.questions.services.question_service import QuestionService

        result = list(QuestionService.get_practice_questions(str(subject.pk), None, 10))
        assert len(result) == 10

    def test_respeita_quantidade_maxima_disponivel(self, questions, subject):
        from apps.questions.services.question_service import QuestionService

        result = list(QuestionService.get_practice_questions(str(subject.pk), None, 50))
        assert len(result) == 15  # só 15 disponíveis

    def test_count_available(self, questions, subject):
        from apps.questions.services.question_service import QuestionService

        assert QuestionService.count_available(str(subject.pk), None) == 15


# ── QuizService.create_practice_quiz ────────────────────────────────────── #


class TestQuizServiceCreate:
    def test_cria_quiz_com_perguntas(self, user, questions, subject):
        from apps.exams.models import Quiz, QuizQuestion
        from apps.exams.services.quiz_service import QuizService

        quiz = QuizService.create_practice_quiz(
            user=user,
            subject_id=str(subject.pk),
            topic_id=None,
            quantity=10,
        )

        assert quiz.status == Quiz.IN_PROGRESS
        assert quiz.quiz_type == Quiz.PRACTICE
        assert quiz.subject == subject
        assert QuizQuestion.objects.filter(quiz=quiz).count() == 10

    def test_quantidade_limitada_ao_disponivel(self, user, questions, subject):
        from apps.exams.services.quiz_service import QuizService

        quiz = QuizService.create_practice_quiz(
            user=user,
            subject_id=str(subject.pk),
            topic_id=None,
            quantity=50,
        )
        assert quiz.quantity == 15


# ── QuizService.submit_answers ───────────────────────────────────────────── #


class TestQuizServiceSubmit:
    def _make_quiz(self, user, subject, questions):
        from apps.exams.services.quiz_service import QuizService

        return QuizService.create_practice_quiz(
            user=user,
            subject_id=str(subject.pk),
            topic_id=None,
            quantity=5,
        )

    def test_resposta_correta_marca_is_correct(self, user, questions, subject):
        from apps.exams.models import Quiz, UserAnswer
        from apps.exams.services.quiz_service import QuizService

        quiz = self._make_quiz(user, subject, questions)
        qq = quiz.quiz_questions.first()
        correct_alt = qq.question.alternatives.get(is_correct=True)

        QuizService.submit_answers(quiz, {str(qq.question.pk): str(correct_alt.pk)})

        ua = UserAnswer.objects.get(quiz=quiz, question=qq.question)
        assert ua.is_correct is True
        quiz.refresh_from_db()
        assert quiz.status == Quiz.FINISHED

    def test_resposta_errada_marca_is_correct_false(self, user, questions, subject):
        from apps.exams.models import UserAnswer
        from apps.exams.services.quiz_service import QuizService

        quiz = self._make_quiz(user, subject, questions)
        qq = quiz.quiz_questions.first()
        wrong_alt = qq.question.alternatives.get(letter="A")  # A não é a correta (D é)

        QuizService.submit_answers(quiz, {str(qq.question.pk): str(wrong_alt.pk)})

        ua = UserAnswer.objects.get(quiz=quiz, question=qq.question)
        assert ua.is_correct is False

    def test_questao_pulada_is_correct_false(self, user, questions, subject):
        from apps.exams.models import UserAnswer
        from apps.exams.services.quiz_service import QuizService

        quiz = self._make_quiz(user, subject, questions)
        QuizService.submit_answers(quiz, {})  # nenhuma resposta

        unanswered = UserAnswer.objects.filter(quiz=quiz, selected_alternative=None)
        assert unanswered.count() == 5

    def test_submit_em_quiz_ja_finalizado_nao_duplica(self, user, questions, subject):
        from apps.exams.models import UserAnswer
        from apps.exams.services.quiz_service import QuizService

        quiz = self._make_quiz(user, subject, questions)
        QuizService.submit_answers(quiz, {})
        count_before = UserAnswer.objects.filter(quiz=quiz).count()

        quiz.refresh_from_db()
        QuizService.submit_answers(quiz, {})
        assert UserAnswer.objects.filter(quiz=quiz).count() == count_before


# ── QuizService.get_result ───────────────────────────────────────────────── #


class TestQuizServiceResult:
    def test_calcula_percentual_correto(self, user, questions, subject):
        from apps.exams.services.quiz_service import QuizService

        quiz = QuizService.create_practice_quiz(
            user=user,
            subject_id=str(subject.pk),
            topic_id=None,
            quantity=4,
        )
        # Responde todas corretamente
        answers = {}
        for qq in quiz.quiz_questions.all():
            correct = qq.question.alternatives.get(is_correct=True)
            answers[str(qq.question.pk)] = str(correct.pk)

        QuizService.submit_answers(quiz, answers)
        result = QuizService.get_result(quiz)

        assert result.correct == 4
        assert result.wrong == 0
        assert result.percentage == 100.0


# ── Regressão de performance (N+1) ───────────────────────────────────────── #


class TestQuizServiceSubmitQueries:
    """Garante que submit_answers não regride para N+1 queries."""

    @staticmethod
    def _answer_all(quiz):
        return {
            str(qq.question.pk): str(qq.question.alternatives.get(is_correct=True).pk)
            for qq in quiz.quiz_questions.all()
        }

    def test_submit_usa_numero_constante_de_queries(self, user, questions, subject):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        from apps.exams.services.quiz_service import QuizService

        quiz_small = QuizService.create_practice_quiz(
            user=user, subject_id=str(subject.pk), topic_id=None, quantity=3
        )
        answers_small = self._answer_all(quiz_small)
        with CaptureQueriesContext(connection) as ctx_small:
            QuizService.submit_answers(quiz_small, answers_small)

        quiz_large = QuizService.create_practice_quiz(
            user=user, subject_id=str(subject.pk), topic_id=None, quantity=12
        )
        answers_large = self._answer_all(quiz_large)
        with CaptureQueriesContext(connection) as ctx_large:
            QuizService.submit_answers(quiz_large, answers_large)

        # Sem N+1: responder 12 questões custa o mesmo nº de queries que 3.
        assert len(ctx_small.captured_queries) == len(ctx_large.captured_queries)
