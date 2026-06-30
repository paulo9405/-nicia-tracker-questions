import pytest

from apps.exams.models import Quiz, QuizQuestion
from apps.questions.models import Alternative, Question, Subject, Topic
from apps.study_plan.models import StudyChapter, StudyModule
from apps.study_plan.services.mini_quiz_service import MiniQuizService


@pytest.fixture
def subject(db):
    return Subject.objects.create(name="Zoonoses", slug="zoonoses", is_active=True)


@pytest.fixture
def topic(db, subject):
    return Topic.objects.create(name="Raiva", slug="raiva", subject=subject, is_active=True)


@pytest.fixture
def questions(db, subject, topic):
    qs = []
    for i in range(5):
        q = Question.objects.create(
            subject=subject,
            topic=topic,
            text=f"Questão {i + 1} sobre raiva",
            external_id=f"test-q-{i + 1}",
            is_active=True,
        )
        for j, letter in enumerate("ABCD"):
            Alternative.objects.create(
                question=q,
                letter=letter,
                text=f"Alternativa {letter}",
                is_correct=(j == 0),
            )
        qs.append(q)
    return qs


@pytest.fixture
def module(db, subject):
    m = StudyModule.objects.create(
        title="Zoonoses",
        slug="zoonoses-mod",
        order=1,
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
        title="Raiva",
        slug="raiva-cap",
        order=1,
        estimated_minutes=30,
        tags=["raiva"],
    )
    ch.related_subjects.add(subject)
    return ch


@pytest.mark.django_db
def test_get_questions_por_topic(user, chapter, questions, topic):
    """Encontra questões via topic matching a tag."""
    result = MiniQuizService.get_questions_for_chapter(chapter)
    assert len(result) >= 3


@pytest.mark.django_db
def test_get_questions_fallback_subject(user, chapter, questions):
    """Fallback para subject do módulo quando não há topic match."""
    chapter.tags = ["tema-inexistente"]
    chapter.save()
    result = MiniQuizService.get_questions_for_chapter(chapter)
    # Deve cair no fallback de subject (module.subject = subject com 5 questões)
    assert len(result) >= 3


@pytest.mark.django_db
def test_get_questions_fallback_related_subjects(db, questions, subject):
    """Fallback para related_subjects quando subject do módulo não está setado."""
    module_sem_subject = StudyModule.objects.create(
        title="Módulo Sem Subject",
        slug="sem-subject",
        order=99,
        master_file="x.md",
        category="specific",
        study_phase="1",
        estimated_hours=1.0,
    )
    chapter_sem_subject = StudyChapter.objects.create(
        module=module_sem_subject,
        title="Cap",
        slug="cap-sem-subject",
        order=1,
        tags=["tema-inexistente"],
    )
    chapter_sem_subject.related_subjects.add(subject)
    result = MiniQuizService.get_questions_for_chapter(chapter_sem_subject)
    assert len(result) >= 3


@pytest.mark.django_db
def test_retorna_vazio_sem_questoes(db, module):
    """Retorna lista vazia quando não há questões suficientes."""
    chapter_vazio = StudyChapter.objects.create(
        module=module,
        title="Cap Vazio",
        slug="cap-vazio",
        order=99,
        tags=["tema-que-nao-existe"],
    )
    # module.subject existe mas não tem questões
    result = MiniQuizService.get_questions_for_chapter(chapter_vazio)
    assert len(result) == 0


@pytest.mark.django_db
def test_create_mini_quiz(user, chapter, questions):
    """Cria Quiz com quiz_type=MINI e QuizQuestion relacionados."""
    quiz = MiniQuizService.create_mini_quiz(user, chapter)
    assert quiz is not None
    assert quiz.quiz_type == Quiz.MINI
    assert quiz.chapter == chapter
    assert quiz.status == Quiz.IN_PROGRESS
    assert QuizQuestion.objects.filter(quiz=quiz).count() >= 3


@pytest.mark.django_db
def test_create_mini_quiz_retorna_none_sem_questoes(user, db, module):
    """Retorna None quando não há questões suficientes."""
    chapter_vazio = StudyChapter.objects.create(
        module=module,
        title="Capítulo Vazio",
        slug="cap-vazio-2",
        order=88,
        tags=["inexistente-xyz"],
    )
    quiz = MiniQuizService.create_mini_quiz(user, chapter_vazio)
    assert quiz is None


@pytest.mark.django_db
def test_count_available_questions(user, chapter, questions):
    count = MiniQuizService.count_available_questions(chapter)
    assert count >= 3
