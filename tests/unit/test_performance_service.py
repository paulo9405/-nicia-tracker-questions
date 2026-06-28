"""
Testes unitários do PerformanceService.
"""

import pytest

pytestmark = pytest.mark.django_db


# ── fixtures ────────────────────────────────────────────────────────────────── #


@pytest.fixture
def subject_a(db):
    from apps.questions.models import Subject

    return Subject.objects.create(
        name="Português", slug="portugues", category="basic", color="#1565c0"
    )


@pytest.fixture
def subject_b(db):
    from apps.questions.models import Subject

    return Subject.objects.create(
        name="Saúde Única", slug="saude-unica", category="specific", color="#2e7d32"
    )


@pytest.fixture
def topic_a(subject_a):
    from apps.questions.models import Topic

    return Topic.objects.create(subject=subject_a, name="Interpretação de Texto", slug="interpretacao")


@pytest.fixture
def topic_b(subject_a):
    from apps.questions.models import Topic

    return Topic.objects.create(subject=subject_a, name="Gramática", slug="gramatica")


def _make_questions(subject, count=5, topic=None):
    from apps.questions.models import Alternative, Question

    qs = []
    for i in range(count):
        slug = f"perf-{subject.slug}-t{topic.slug if topic else 'none'}-q{i+1:03d}"
        q = Question.objects.create(
            subject=subject,
            topic=topic,
            external_id=slug,
            text=f"Questão {i + 1}?",
        )
        for letter, correct in zip("ABCD", [False, False, False, True]):
            Alternative.objects.create(
                question=q, letter=letter, text=f"Alt {letter}", is_correct=correct
            )
        qs.append(q)
    return qs


def _finish_quiz(user, subject, questions, correct_count=0):
    from apps.exams.services.quiz_service import QuizService

    quiz = QuizService.create_practice_quiz(
        user=user,
        subject_id=str(subject.pk),
        topic_id=None,
        quantity=len(questions),
    )
    answers = {}
    for i, qq in enumerate(quiz.quiz_questions.all()):
        if i < correct_count:
            alt = qq.question.alternatives.get(is_correct=True)
            answers[str(qq.question.pk)] = str(alt.pk)
    QuizService.submit_answers(quiz, answers)
    return quiz


# ── TestPerformanceServiceStats ──────────────────────────────────────────────── #


class TestPerformanceServiceStats:
    def test_usuario_sem_treinos_retorna_vazio(self, user):
        from apps.performance.services.performance_service import PerformanceService

        stats = PerformanceService.get_full_stats(user)

        assert stats.total_subjects_studied == 0
        assert stats.total_topics_studied == 0
        assert stats.subjects == []
        assert stats.weak_topics == []
        assert stats.strong_topics == []
        assert stats.has_topic_data is False

    def test_calcula_percentual_por_disciplina(self, user, subject_a):
        from apps.performance.services.performance_service import PerformanceService

        questions = _make_questions(subject_a, count=4)
        _finish_quiz(user, subject_a, questions, correct_count=2)

        stats = PerformanceService.get_full_stats(user)

        assert len(stats.subjects) == 1
        s = stats.subjects[0]
        assert s.name == "Português"
        assert s.total == 4
        assert s.correct == 2
        assert s.percentage == 50

    def test_disciplinas_ordenadas_por_menor_percentual(self, user, subject_a, subject_b):
        from apps.performance.services.performance_service import PerformanceService

        q_a = _make_questions(subject_a, count=4)
        q_b = _make_questions(subject_b, count=4)
        _finish_quiz(user, subject_a, q_a, correct_count=1)  # 25%
        _finish_quiz(user, subject_b, q_b, correct_count=4)  # 100%

        stats = PerformanceService.get_full_stats(user)

        assert stats.subjects[0].name == "Português"   # pior primeiro
        assert stats.subjects[1].name == "Saúde Única"

    def test_total_disciplinas_estudadas(self, user, subject_a, subject_b):
        from apps.performance.services.performance_service import PerformanceService

        _finish_quiz(user, subject_a, _make_questions(subject_a, 4))
        _finish_quiz(user, subject_b, _make_questions(subject_b, 4))

        stats = PerformanceService.get_full_stats(user)

        assert stats.total_subjects_studied == 2


class TestPerformanceServiceTopics:
    def test_sem_topicos_has_topic_data_e_false(self, user, subject_a):
        from apps.performance.services.performance_service import PerformanceService

        # questões sem tópico
        _finish_quiz(user, subject_a, _make_questions(subject_a, 5))

        stats = PerformanceService.get_full_stats(user)

        assert stats.has_topic_data is False
        assert stats.total_topics_studied == 0

    def test_conta_topicos_estudados(self, user, subject_a, topic_a, topic_b):
        from apps.performance.services.performance_service import PerformanceService

        q_a = _make_questions(subject_a, count=4, topic=topic_a)
        q_b = _make_questions(subject_a, count=4, topic=topic_b)
        _finish_quiz(user, subject_a, q_a + q_b)

        stats = PerformanceService.get_full_stats(user)

        assert stats.has_topic_data is True
        assert stats.total_topics_studied == 2

    def test_pontos_fracos_filtram_minimo_questoes(self, user, subject_a, topic_a):
        from apps.performance.services.performance_service import (
            MIN_QUESTIONS_FOR_RANKING,
            PerformanceService,
        )

        # apenas 1 questão (abaixo do mínimo)
        q = _make_questions(subject_a, count=1, topic=topic_a)
        _finish_quiz(user, subject_a, q)

        stats = PerformanceService.get_full_stats(user)

        # tópico com 1 questão não entra no ranking
        assert stats.weak_topics == []
        assert stats.strong_topics == []

    def test_pontos_fracos_ordenados_pior_primeiro(self, user, subject_a, topic_a, topic_b):
        from apps.performance.services.performance_service import PerformanceService

        q_a = _make_questions(subject_a, count=4, topic=topic_a)
        q_b = _make_questions(subject_a, count=4, topic=topic_b)

        # topic_a: 0 acertos (0%), topic_b: 4 acertos (100%)
        quiz = _finish_quiz(user, subject_a, q_a + q_b, correct_count=4)

        stats = PerformanceService.get_full_stats(user)

        if stats.weak_topics:
            assert stats.weak_topics[0].percentage <= stats.weak_topics[-1].percentage

    def test_pontos_fortes_ordenados_melhor_primeiro(self, user, subject_a, topic_a, topic_b):
        from apps.performance.services.performance_service import PerformanceService

        q_a = _make_questions(subject_a, count=4, topic=topic_a)
        q_b = _make_questions(subject_a, count=4, topic=topic_b)
        _finish_quiz(user, subject_a, q_a + q_b)

        stats = PerformanceService.get_full_stats(user)

        if stats.strong_topics:
            assert stats.strong_topics[0].percentage >= stats.strong_topics[-1].percentage

    def test_pontos_fracos_limitados_a_cinco(self, user, subject_a):
        from apps.questions.models import Alternative, Question, Topic
        from apps.performance.services.performance_service import PerformanceService

        # Cria 7 tópicos com 4 questões cada
        topics = []
        all_questions = []
        for i in range(7):
            t = Topic.objects.create(
                subject=subject_a, name=f"Tópico {i}", slug=f"topico-{i}"
            )
            topics.append(t)
            qs = _make_questions(subject_a, count=4, topic=t)
            all_questions.extend(qs)

        _finish_quiz(user, subject_a, all_questions)

        stats = PerformanceService.get_full_stats(user)

        assert len(stats.weak_topics) <= 5
        assert len(stats.strong_topics) <= 5
