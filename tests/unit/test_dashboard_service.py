"""
Testes unitários do DashboardService.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


# ── fixtures ────────────────────────────────────────────────────────────────── #


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
    for i in range(10):
        q = Question.objects.create(
            subject=subject,
            external_id=f"dash-s01-q{i+1:03d}",
            text=f"Enunciado {i + 1}?",
        )
        for letter, correct in zip("ABCD", [False, False, False, True]):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
            )
        qs.append(q)
    return qs


def _make_finished_quiz(user, subject, questions, all_correct=False):
    from apps.exams.services.quiz_service import QuizService

    quiz = QuizService.create_practice_quiz(
        user=user,
        subject_id=str(subject.pk),
        topic_id=None,
        quantity=5,
    )
    if all_correct:
        answers = {
            str(qq.question.pk): str(qq.question.alternatives.get(is_correct=True).pk)
            for qq in quiz.quiz_questions.all()
        }
    else:
        answers = {}
    QuizService.submit_answers(quiz, answers)
    return quiz


# ── TestDashboardServiceStats ────────────────────────────────────────────────── #


class TestDashboardServiceStats:
    def test_novo_usuario_retorna_zeros(self, user):
        from apps.dashboard.services.dashboard_service import DashboardService

        stats = DashboardService.get_stats(user)

        assert stats.total_answered == 0
        assert stats.total_correct == 0
        assert stats.total_wrong == 0
        assert stats.total_quizzes == 0
        assert stats.streak == 0
        assert stats.overall_percentage == 0
        assert stats.subject_stats == []
        assert stats.recent_quizzes == []

    def test_conta_questoes_respondidas(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions)

        stats = DashboardService.get_stats(user)

        assert stats.total_answered == 5
        assert stats.total_quizzes == 1

    def test_conta_acertos_erros_e_percentual(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions, all_correct=True)

        stats = DashboardService.get_stats(user)

        assert stats.total_correct == 5
        assert stats.total_wrong == 0
        assert stats.overall_percentage == 100

    def test_percentual_com_erros(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions, all_correct=False)

        stats = DashboardService.get_stats(user)

        # todas puladas = todas erradas
        assert stats.total_correct == 0
        assert stats.total_wrong == 5
        assert stats.overall_percentage == 0

    def test_subject_stats_calculados(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions, all_correct=True)

        stats = DashboardService.get_stats(user)

        assert len(stats.subject_stats) == 1
        s = stats.subject_stats[0]
        assert s.name == "Saúde Única"
        assert s.total == 5
        assert s.correct == 5
        assert s.percentage == 100

    def test_acumulado_de_varios_quizzes(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions)
        _make_finished_quiz(user, subject, questions)

        stats = DashboardService.get_stats(user)

        assert stats.total_answered == 10
        assert stats.total_quizzes == 2

    def test_recent_quizzes_limita_a_cinco(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        for _ in range(7):
            _make_finished_quiz(user, subject, questions)

        stats = DashboardService.get_stats(user)

        assert len(stats.recent_quizzes) == 5


# ── TestDashboardServiceStreak ───────────────────────────────────────────────── #


class TestDashboardServiceStreak:
    def test_streak_sem_treinos_e_zero(self, user):
        from apps.dashboard.services.dashboard_service import DashboardService

        stats = DashboardService.get_stats(user)

        assert stats.streak == 0

    def test_streak_com_treino_hoje(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        _make_finished_quiz(user, subject, questions)

        stats = DashboardService.get_stats(user)

        assert stats.streak == 1

    def test_streak_quebrado_por_dia_sem_treino(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        quiz = _make_finished_quiz(user, subject, questions)
        # Simula treino há 3 dias
        quiz.finished_at = timezone.now() - timedelta(days=3)
        quiz.save(update_fields=["finished_at"])

        stats = DashboardService.get_stats(user)

        assert stats.streak == 0

    def test_streak_dois_dias_consecutivos(self, user, subject, questions):
        from apps.dashboard.services.dashboard_service import DashboardService

        quiz1 = _make_finished_quiz(user, subject, questions)
        quiz2 = _make_finished_quiz(user, subject, questions)

        # quiz1 = ontem, quiz2 = hoje
        quiz1.finished_at = timezone.now() - timedelta(days=1)
        quiz1.save(update_fields=["finished_at"])
        quiz2.finished_at = timezone.now()
        quiz2.save(update_fields=["finished_at"])

        stats = DashboardService.get_stats(user)

        assert stats.streak == 2
