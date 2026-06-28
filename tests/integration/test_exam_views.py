"""
Testes de integração das views do módulo de questões (Fase 5).
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# ── Fixtures ─────────────────────────────────────────────────────────────── #


@pytest.fixture
def subject(db):
    from apps.questions.models import Subject

    return Subject.objects.create(
        name="Saúde Única", slug="saude-unica", category="specific"
    )


@pytest.fixture
def questions(subject):
    from apps.questions.models import Alternative, Question

    qs = []
    for i in range(12):
        q = Question.objects.create(
            subject=subject,
            external_id=f"view-s01-q{i+1:03d}",
            text=f"Questão {i + 1}?",
        )
        for j, letter in enumerate("ABCD"):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt {letter}", is_correct=(j == 3)
            )
        qs.append(q)
    return qs


@pytest.fixture
def quiz(user, subject, questions):
    from apps.exams.services.quiz_service import QuizService

    return QuizService.create_practice_quiz(
        user=user, subject_id=str(subject.pk), topic_id=None, quantity=5
    )


# ── FilterView ──────────────────────────────────────────────────────────── #


class TestFilterView:
    url = reverse("exams:filter")

    def test_redireciona_nao_autenticado(self, client):
        r = client.get(self.url)
        assert r.status_code == 302

    def test_get_exibe_formulario(self, client_logged):
        r = client_logged.get(self.url)
        assert r.status_code == 200
        assert "form" in r.context

    def test_post_cria_quiz_e_redireciona_para_play(self, client_logged, subject, questions):
        data = {"subject": str(subject.pk), "quantity": "10"}
        r = client_logged.post(self.url, data)
        assert r.status_code == 302
        assert "/treino/" in r.url

    def test_post_sem_disciplina_retorna_form_invalido(self, client_logged):
        r = client_logged.post(self.url, {"quantity": "10"})
        assert r.status_code == 200
        assert r.context["form"].errors


# ── PlayQuizView ─────────────────────────────────────────────────────────── #


class TestPlayQuizView:
    def test_get_exibe_questoes(self, client_logged, quiz):
        url = reverse("exams:play", kwargs={"pk": quiz.pk})
        r = client_logged.get(url)
        assert r.status_code == 200
        assert "quiz_questions" in r.context

    def test_outro_usuario_recebe_404(self, client, user, quiz):
        from apps.accounts.models import User

        other = User.objects.create_user(email="other@test.com", password="Pass@1234")
        client.force_login(other)
        url = reverse("exams:play", kwargs={"pk": quiz.pk})
        r = client.get(url)
        assert r.status_code == 404

    def test_post_submete_e_redireciona_para_resultado(self, client_logged, quiz):
        url = reverse("exams:play", kwargs={"pk": quiz.pk})
        r = client_logged.post(url, {})  # responde em branco (tudo pulado)
        assert r.status_code == 302
        assert "/resultado/" in r.url

    def test_quiz_finalizado_redireciona_para_resultado(self, client_logged, quiz):
        from apps.exams.services.quiz_service import QuizService

        QuizService.submit_answers(quiz, {})
        url = reverse("exams:play", kwargs={"pk": quiz.pk})
        r = client_logged.get(url)
        assert r.status_code == 302
        assert "/resultado/" in r.url


# ── ResultView ───────────────────────────────────────────────────────────── #


class TestResultView:
    def _finish(self, quiz):
        from apps.exams.services.quiz_service import QuizService

        QuizService.submit_answers(quiz, {})
        return quiz

    def test_get_exibe_resultado(self, client_logged, quiz):
        self._finish(quiz)
        url = reverse("exams:result", kwargs={"pk": quiz.pk})
        r = client_logged.get(url)
        assert r.status_code == 200
        assert "result" in r.context

    def test_quiz_nao_finalizado_redireciona_para_play(self, client_logged, quiz):
        url = reverse("exams:result", kwargs={"pk": quiz.pk})
        r = client_logged.get(url)
        assert r.status_code == 302
        assert "/treino/" in r.url

    def test_result_contem_todos_os_items(self, client_logged, quiz):
        self._finish(quiz)
        url = reverse("exams:result", kwargs={"pk": quiz.pk})
        r = client_logged.get(url)
        assert r.context["result"].total == 5
