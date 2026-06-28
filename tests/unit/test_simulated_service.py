"""
Testes unitários do SimulatedService.
"""

import pytest

pytestmark = pytest.mark.django_db


# ── helpers ─────────────────────────────────────────────────────────────────── #


def _make_subject(name, slug, category, color="#888888"):
    from apps.questions.models import Subject

    return Subject.objects.create(name=name, slug=slug, category=category, color=color)


def _add_questions(subject, count):
    from apps.questions.models import Alternative, Question

    qs = []
    for i in range(count):
        q = Question.objects.create(
            subject=subject,
            external_id=f"sim-{subject.slug}-q{i:03d}",
            text=f"Questão {i + 1}?",
        )
        for letter, correct in zip("ABCD", [False, False, False, True]):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
            )
        qs.append(q)
    return qs


@pytest.fixture
def full_bank(db):
    """Cria o banco mínimo para um simulado completo."""
    # 4 disciplinas básicas com 10 questões cada (precisa de ≥5)
    basics = [
        _make_subject("Português", "portugues", "basic", "#1565c0"),
        _make_subject("Matemática", "matematica", "basic", "#c62828"),
        _make_subject("Informática", "informatica", "basic", "#6a1b9a"),
        _make_subject("Conhecimentos Gerais", "conhecimentos-gerais", "basic", "#ef6c00"),
    ]
    for s in basics:
        _add_questions(s, 10)

    # 1 disciplina específica com 25 questões (precisa de ≥20)
    specific = _make_subject("Saúde Única", "saude-unica", "specific", "#2e7d32")
    _add_questions(specific, 25)

    return {"basics": basics, "specific": specific}


# ── TestSimulatedServiceCreate ────────────────────────────────────────────────── #


class TestSimulatedServiceCreate:
    def test_cria_quiz_com_40_questoes(self, user, full_bank):
        from apps.exams.models import Quiz, QuizQuestion
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)

        assert quiz.quiz_type == Quiz.SIMULATED
        assert quiz.status == Quiz.IN_PROGRESS
        assert quiz.quantity == 40
        assert quiz.subject is None  # simulado não tem disciplina única
        assert QuizQuestion.objects.filter(quiz=quiz).count() == 40

    def test_distribuicao_20_basicas_20_especificas(self, user, full_bank):
        from apps.exams.models import QuizQuestion
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)

        from apps.questions.models import Subject

        basic_pks = set(
            Subject.objects.filter(category="basic").values_list("pk", flat=True)
        )
        qqs = QuizQuestion.objects.filter(quiz=quiz).select_related("question__subject")

        basic_count = sum(
            1 for qq in qqs if qq.question.subject_id in basic_pks
        )
        specific_count = quiz.quantity - basic_count

        assert basic_count == 20
        assert specific_count == 20

    def test_raises_sem_questoes_basicas_suficientes(self, user, db):
        from apps.exams.services.simulated_service import (
            InsufficientQuestionsError,
            SimulatedService,
        )

        # Cria disciplina básica com apenas 2 questões (precisa de 5)
        s = _make_subject("Português", "portugues", "basic")
        _add_questions(s, 2)

        with pytest.raises(InsufficientQuestionsError):
            SimulatedService.create_simulated_quiz(user)

    def test_raises_sem_questoes_especificas_suficientes(self, user, db):
        from apps.exams.services.simulated_service import (
            InsufficientQuestionsError,
            SimulatedService,
        )

        # 4 básicas ok, mas apenas 5 específicas (precisa de 20)
        for name, slug, color in [
            ("Português", "portugues", "#1565c0"),
            ("Matemática", "matematica", "#c62828"),
            ("Informática", "informatica", "#6a1b9a"),
            ("Conhecimentos Gerais", "conhecimentos-gerais", "#ef6c00"),
        ]:
            s = _make_subject(name, slug, "basic", color)
            _add_questions(s, 10)

        spec = _make_subject("Específica", "especifica", "specific")
        _add_questions(spec, 5)

        with pytest.raises(InsufficientQuestionsError):
            SimulatedService.create_simulated_quiz(user)

    def test_questoes_em_ordem_valida(self, user, full_bank):
        from apps.exams.models import QuizQuestion
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        orders = list(
            QuizQuestion.objects.filter(quiz=quiz)
            .values_list("order", flat=True)
            .order_by("order")
        )
        assert orders == list(range(1, 41))


# ── TestSimulatedServiceInProgress ───────────────────────────────────────────── #


class TestSimulatedServiceInProgress:
    def test_retorna_none_sem_simulado_ativo(self, user, db):
        from apps.exams.services.simulated_service import SimulatedService

        assert SimulatedService.get_in_progress(user) is None

    def test_retorna_simulado_em_andamento(self, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        found = SimulatedService.get_in_progress(user)

        assert found is not None
        assert found.pk == quiz.pk

    def test_nao_retorna_simulado_finalizado(self, user, full_bank):
        from apps.exams.services.simulated_service import SimulatedService
        from apps.exams.services.quiz_service import QuizService

        quiz = SimulatedService.create_simulated_quiz(user)
        QuizService.submit_answers(quiz, {})

        assert SimulatedService.get_in_progress(user) is None


# ── TestSimulatedServiceBreakdown ─────────────────────────────────────────────── #


class TestSimulatedServiceBreakdown:
    def test_breakdown_por_disciplina(self, user, full_bank):
        from apps.exams.services.quiz_service import QuizService
        from apps.exams.services.simulated_service import SimulatedService

        quiz = SimulatedService.create_simulated_quiz(user)
        QuizService.submit_answers(quiz, {})

        breakdown = SimulatedService.get_subject_breakdown(quiz)

        assert len(breakdown) >= 2  # ao menos básicas + específica

        for entry in breakdown:
            assert "name" in entry
            assert "total" in entry
            assert "correct" in entry
            assert "percentage" in entry
            assert 0 <= entry["percentage"] <= 100
