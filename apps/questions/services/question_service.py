"""
QuestionService — consultas e seleção de questões para treino.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.questions.models import Question, Subject, Topic


class QuestionService:

    @staticmethod
    def get_active_subjects() -> QuerySet:
        return Subject.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def get_topics_for_subject(subject_id) -> QuerySet:
        return Topic.objects.filter(subject_id=subject_id, is_active=True).order_by("name")

    @staticmethod
    def get_practice_questions(
        subject_id: str,
        topic_id: str | None,
        quantity: int,
    ) -> QuerySet:
        """
        Retorna questões aleatórias para treino.
        Se disponíveis < quantity, retorna todas as disponíveis.
        """
        qs = Question.objects.filter(subject_id=subject_id, is_active=True)
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        qs = qs.prefetch_related("alternatives").order_by("?")
        return qs[:quantity]

    @staticmethod
    def count_available(subject_id: str, topic_id: str | None) -> int:
        qs = Question.objects.filter(subject_id=subject_id, is_active=True)
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs.count()
