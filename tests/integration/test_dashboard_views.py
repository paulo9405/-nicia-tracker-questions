"""
Testes de integração das views do Dashboard.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestDashboardView:
    def test_requer_login(self, client):
        r = client.get("/")
        assert r.status_code == 302
        assert "login" in r.url

    def test_carrega_para_usuario_autenticado(self, client_logged):
        r = client_logged.get("/")
        assert r.status_code == 200

    def test_contexto_contem_stats(self, client_logged):
        r = client_logged.get("/")
        assert "stats" in r.context

    def test_stats_zeradas_para_novo_usuario(self, client_logged):
        r = client_logged.get("/")
        stats = r.context["stats"]
        assert stats.total_answered == 0
        assert stats.total_quizzes == 0
        assert stats.streak == 0

    def test_exibe_empty_state_sem_treinos(self, client_logged):
        r = client_logged.get("/")
        assert b"Bem-vindo ao N\xc3\xadcia Track" in r.content

    def test_exibe_metricas_com_treinos(self, client_logged, user):
        from apps.exams.services.quiz_service import QuizService
        from apps.questions.models import Alternative, Question, Subject

        subject = Subject.objects.create(
            name="Português", slug="portugues", category="basic"
        )
        for i in range(5):
            q = Question.objects.create(
                subject=subject,
                external_id=f"dv-s01-q{i+1:03d}",
                text=f"Questão {i+1}?",
            )
            for letter, correct in zip("ABCD", [False, False, False, True]):
                Alternative.objects.create(
                    question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
                )

        quiz = QuizService.create_practice_quiz(
            user=user,
            subject_id=str(subject.pk),
            topic_id=None,
            quantity=5,
        )
        QuizService.submit_answers(quiz, {})

        r = client_logged.get("/")
        stats = r.context["stats"]
        assert stats.total_answered == 5
        assert stats.total_quizzes == 1

    def test_dashboard_url_reversivel(self):
        from django.urls import reverse

        assert reverse("dashboard:home") == "/"
