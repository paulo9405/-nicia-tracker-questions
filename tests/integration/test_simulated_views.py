"""
Testes de integração das views de Simulado.
"""

import pytest

pytestmark = pytest.mark.django_db


# ── fixture do banco completo ────────────────────────────────────────────────── #


def _make_subject(name, slug, category, color="#888888"):
    from apps.questions.models import Subject

    return Subject.objects.create(name=name, slug=slug, category=category, color=color)


def _add_questions(subject, count):
    from apps.questions.models import Alternative, Question

    for i in range(count):
        q = Question.objects.create(
            subject=subject,
            external_id=f"sv-{subject.slug}-q{i:03d}",
            text=f"Q{i + 1}?",
        )
        for letter, correct in zip("ABCD", [False, False, False, True]):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt", is_correct=correct
            )


@pytest.fixture
def full_bank(db):
    for name, slug, color in [
        ("Português", "portugues-sv", "#1565c0"),
        ("Matemática", "matematica-sv", "#c62828"),
        ("Informática", "informatica-sv", "#6a1b9a"),
        ("Conhecimentos Gerais", "conhecimentos-gerais-sv", "#ef6c00"),
    ]:
        s = _make_subject(name, slug, "basic", color)
        _add_questions(s, 10)

    spec = _make_subject("Saúde Única", "saude-unica-sv", "specific", "#2e7d32")
    _add_questions(spec, 25)


# ── TestSimulatedStartView ────────────────────────────────────────────────────── #


class TestSimulatedStartView:
    def test_requer_login(self, client):
        r = client.get("/questoes/simulado/")
        assert r.status_code == 302
        assert "login" in r.url

    def test_exibe_pagina_de_inicio(self, client_logged):
        r = client_logged.get("/questoes/simulado/")
        assert r.status_code == 200
        assert b"Simulado" in r.content

    def test_post_cria_simulado_e_redireciona(self, client_logged, full_bank):
        r = client_logged.post("/questoes/simulado/")
        assert r.status_code == 302
        assert "/questoes/simulado/" in r.url

    def test_get_com_simulado_ativo_redireciona(self, client_logged, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        r = client_logged.get("/questoes/simulado/")
        assert r.status_code == 302
        assert str(quiz.pk) in r.url

    def test_url_reversivel(self):
        from django.urls import reverse

        assert reverse("exams:simulated_start") == "/questoes/simulado/"


# ── TestSimulatedPlayView ─────────────────────────────────────────────────────── #


class TestSimulatedPlayView:
    def test_requer_login(self, client, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        r = client.get(f"/questoes/simulado/{quiz.pk}/")
        assert r.status_code == 302
        assert "login" in r.url

    def test_exibe_40_questoes(self, client_logged, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        r = client_logged.get(f"/questoes/simulado/{quiz.pk}/")
        assert r.status_code == 200
        assert len(r.context["quiz_questions"]) == 40

    def test_tem_time_limit_no_contexto(self, client_logged, user, full_bank):
        from apps.exams.services.simulated_service import (
            TIME_LIMIT_MINUTES,
            SimulatedService,
        )

        quiz = SimulatedService.create_simulated_quiz(user)
        r = client_logged.get(f"/questoes/simulado/{quiz.pk}/")
        assert r.context["time_limit_minutes"] == TIME_LIMIT_MINUTES

    def test_post_finaliza_e_redireciona_para_resultado(
        self, client_logged, user, full_bank
    ):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        r = client_logged.post(f"/questoes/simulado/{quiz.pk}/")
        assert r.status_code == 302
        assert f"/questoes/resultado/{quiz.pk}/" in r.url

    def test_resultado_tem_breakdown(self, client_logged, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        client_logged.post(f"/questoes/simulado/{quiz.pk}/")

        r = client_logged.get(f"/questoes/resultado/{quiz.pk}/")
        assert r.status_code == 200
        assert "subject_breakdown" in r.context
        assert len(r.context["subject_breakdown"]) >= 2
