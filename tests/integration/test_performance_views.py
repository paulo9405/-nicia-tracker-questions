"""
Testes de integração das views de Performance.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestPerformanceView:
    def test_requer_login(self, client):
        r = client.get("/estatisticas/")
        assert r.status_code == 302
        assert "login" in r.url

    def test_carrega_para_usuario_autenticado(self, client_logged):
        r = client_logged.get("/estatisticas/")
        assert r.status_code == 200

    def test_contexto_contem_stats(self, client_logged):
        r = client_logged.get("/estatisticas/")
        assert "stats" in r.context

    def test_exibe_empty_state_sem_treinos(self, client_logged):
        r = client_logged.get("/estatisticas/")
        assert b"Nenhuma estat" in r.content

    def test_exibe_disciplinas_com_treinos(self, client_logged, user):
        from apps.questions.models import Alternative, Question, Subject
        from apps.exams.services.quiz_service import QuizService

        subject = Subject.objects.create(
            name="Informática", slug="informatica", category="basic"
        )
        for i in range(4):
            q = Question.objects.create(
                subject=subject,
                external_id=f"pv-s01-q{i+1:03d}",
                text=f"Questão {i+1}?",
            )
            for letter, correct in zip("ABCD", [False, False, False, True]):
                Alternative.objects.create(
                    question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
                )

        quiz = QuizService.create_practice_quiz(
            user=user, subject_id=str(subject.pk), topic_id=None, quantity=4
        )
        QuizService.submit_answers(quiz, {})

        r = client_logged.get("/estatisticas/")
        stats = r.context["stats"]
        assert stats.total_subjects_studied == 1
        assert stats.subjects[0].name == "Informática"

    def test_url_reversivel(self):
        from django.urls import reverse
        assert reverse("performance:stats") == "/estatisticas/"
