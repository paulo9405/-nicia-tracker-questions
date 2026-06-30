from __future__ import annotations

from datetime import date, timedelta

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.exams.models import Quiz, UserAnswer
from apps.study_plan.models import ErrorNotebookEntry, _next_review_date


class ErrorNotebookService:

    @staticmethod
    @transaction.atomic
    def sync_errors(user, quiz: Quiz) -> int:
        """
        Percorre os UserAnswer errados do quiz e faz upsert em ErrorNotebookEntry.
        Questões puladas (selected_alternative=None) são ignoradas.
        Retorna o número de entradas criadas ou atualizadas.
        """
        wrong_answers = list(
            UserAnswer.objects.filter(
                quiz=quiz,
                is_correct=False,
            )
            .exclude(selected_alternative__isnull=True)
            .select_related("question")
        )

        synced = 0
        for ua in wrong_answers:
            entry, created = ErrorNotebookEntry.objects.get_or_create(
                user=user,
                question=ua.question,
                defaults={
                    "last_user_answer": ua,
                    "wrong_count": 1,
                    "last_wrong_at": timezone.now(),
                    "next_review_at": _next_review_date(1),
                },
            )
            if not created:
                entry.wrong_count += 1
                entry.last_user_answer = ua
                entry.last_wrong_at = timezone.now()
                entry.next_review_at = _next_review_date(entry.wrong_count)
                entry.save(update_fields=[
                    "wrong_count", "last_user_answer", "last_wrong_at",
                    "next_review_at", "updated_at",
                ])
            synced += 1

        return synced

    @staticmethod
    def get_notebook(
        user,
        subject_id: str | None = None,
        is_reviewed: bool | None = None,
        order_by: str = "-wrong_count",
    ) -> QuerySet:
        qs = (
            ErrorNotebookEntry.objects.filter(user=user)
            .select_related(
                "question__subject",
                "question__topic",
                "last_user_answer__selected_alternative",
            )
        )
        if subject_id:
            qs = qs.filter(question__subject_id=subject_id)
        if is_reviewed is not None:
            qs = qs.filter(is_reviewed=is_reviewed)

        valid_orderings = {
            "-wrong_count", "wrong_count",
            "-last_wrong_at", "last_wrong_at",
            "next_review_at", "-next_review_at",
        }
        if order_by in valid_orderings:
            qs = qs.order_by(order_by)

        return qs

    @staticmethod
    @transaction.atomic
    def save_personal_note(user, entry_id: str, note: str) -> ErrorNotebookEntry:
        entry = ErrorNotebookEntry.objects.get(id=entry_id, user=user)
        entry.personal_note = note
        entry.save(update_fields=["personal_note", "updated_at"])
        return entry

    @staticmethod
    @transaction.atomic
    def mark_as_reviewed(user, entry_id: str) -> ErrorNotebookEntry:
        entry = ErrorNotebookEntry.objects.get(id=entry_id, user=user)
        entry.is_reviewed = True
        entry.next_review_at = None
        entry.save(update_fields=["is_reviewed", "next_review_at", "updated_at"])
        return entry
