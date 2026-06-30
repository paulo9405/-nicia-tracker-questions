from __future__ import annotations

from django.db import transaction
from django.db.models import Q, QuerySet

from apps.exams.models import Quiz, QuizQuestion
from apps.questions.models import Question, Topic
from apps.study_plan.models import StudyChapter

MIN_QUESTIONS = 3
DEFAULT_QUANTITY = 5


class MiniQuizService:

    @staticmethod
    def _get_questions_by_tags(chapter: StudyChapter, quantity: int) -> QuerySet:
        """Tenta buscar questões via Topics que correspondam às tags do capítulo."""
        tags = chapter.tags or []
        if not tags:
            return Question.objects.none()

        tag_filter = Q()
        for tag in tags:
            tag_filter |= Q(name__icontains=tag)

        topic_ids = Topic.objects.filter(tag_filter).values_list("id", flat=True)
        if not topic_ids:
            return Question.objects.none()

        return (
            Question.objects.filter(topic_id__in=topic_ids, is_active=True)
            .prefetch_related("alternatives")
            .order_by("?")[:quantity]
        )

    @staticmethod
    def _get_questions_by_subject(subject_id: str, quantity: int) -> QuerySet:
        return (
            Question.objects.filter(subject_id=subject_id, is_active=True)
            .prefetch_related("alternatives")
            .order_by("?")[:quantity]
        )

    @staticmethod
    def get_questions_for_chapter(chapter: StudyChapter, quantity: int = DEFAULT_QUANTITY) -> list:
        """
        Retorna lista de questões para o capítulo, usando fallback progressivo:
        1. Por Topic matching tags
        2. Por module.subject
        3. Por related_subjects
        Retorna lista vazia se não encontrar o mínimo.
        """
        # Tentativa 1: por tags → topics
        qs = list(MiniQuizService._get_questions_by_tags(chapter, quantity))
        if len(qs) >= MIN_QUESTIONS:
            return qs[:quantity]

        # Tentativa 2: por subject do módulo
        if chapter.module.subject_id:
            qs = list(MiniQuizService._get_questions_by_subject(
                str(chapter.module.subject_id), quantity
            ))
            if len(qs) >= MIN_QUESTIONS:
                return qs[:quantity]

        # Tentativa 3: por related_subjects
        seen_ids = set()
        combined = []
        for subject in chapter.related_subjects.all():
            batch = list(
                Question.objects.filter(subject=subject, is_active=True)
                .exclude(id__in=seen_ids)
                .prefetch_related("alternatives")
                .order_by("?")[:quantity]
            )
            for q in batch:
                if q.id not in seen_ids:
                    seen_ids.add(q.id)
                    combined.append(q)
            if len(combined) >= quantity:
                break

        if len(combined) >= MIN_QUESTIONS:
            return combined[:quantity]

        return []

    @staticmethod
    def count_available_questions(chapter: StudyChapter) -> int:
        questions = MiniQuizService.get_questions_for_chapter(chapter, quantity=DEFAULT_QUANTITY)
        return len(questions)

    @staticmethod
    @transaction.atomic
    def create_mini_quiz(user, chapter: StudyChapter) -> Quiz | None:
        questions = MiniQuizService.get_questions_for_chapter(chapter)
        if not questions:
            return None

        quiz = Quiz.objects.create(
            user=user,
            chapter=chapter,
            quiz_type=Quiz.MINI,
            status=Quiz.IN_PROGRESS,
            quantity=len(questions),
        )

        QuizQuestion.objects.bulk_create([
            QuizQuestion(quiz=quiz, question=q, order=i + 1)
            for i, q in enumerate(questions)
        ])

        return quiz

    @staticmethod
    def get_suggested_questions(chapter: StudyChapter, limit: int = 5) -> list:
        return MiniQuizService.get_questions_for_chapter(chapter, quantity=limit)
