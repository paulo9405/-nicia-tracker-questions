"""
SimulatedService — criação e análise de simulados.

Distribuição da prova (Concurso 003/2026 — Instituto UniFil):
- 5 questões de cada disciplina básica (Português, Matemática,
  Informática, Conhecimentos Gerais) = 20 questões
- 20 questões distribuídas aleatoriamente entre as disciplinas específicas
= 40 questões no total
"""

from __future__ import annotations

import random

from django.db import transaction
from django.db.models import Count, Q

from apps.core.exceptions import DomainException
from apps.exams.models import Quiz, QuizQuestion, UserAnswer
from apps.questions.models import Question, Subject


BASIC_PER_SUBJECT = 5
SPECIFIC_TOTAL = 20
SIMULATED_TOTAL = 40
TIME_LIMIT_MINUTES = 180


class InsufficientQuestionsError(DomainException):
    pass


class SimulatedService:

    @staticmethod
    def get_in_progress(user) -> Quiz | None:
        """Retorna o simulado em andamento do usuário, ou None."""
        return Quiz.objects.filter(
            user=user,
            quiz_type=Quiz.SIMULATED,
            status=Quiz.IN_PROGRESS,
        ).first()

    @staticmethod
    @transaction.atomic
    def create_simulated_quiz(user) -> Quiz:
        basic_subjects = list(
            Subject.objects.filter(category=Subject.BASIC, is_active=True)
        )

        basic_questions: list[Question] = []
        for subj in basic_subjects:
            qs = list(
                Question.objects.filter(subject=subj, is_active=True)
                .order_by("?")[:BASIC_PER_SUBJECT]
            )
            if len(qs) < BASIC_PER_SUBJECT:
                raise InsufficientQuestionsError(
                    f"Disciplina '{subj.name}' tem apenas {len(qs)} questão(ões) "
                    f"disponível(eis) (mínimo: {BASIC_PER_SUBJECT})."
                )
            basic_questions.extend(qs)

        specific_questions = list(
            Question.objects.filter(
                subject__category=Subject.SPECIFIC,
                is_active=True,
            )
            .order_by("?")[:SPECIFIC_TOTAL]
        )

        if len(specific_questions) < SPECIFIC_TOTAL:
            raise InsufficientQuestionsError(
                f"Questões específicas insuficientes: {len(specific_questions)} "
                f"disponíveis (mínimo: {SPECIFIC_TOTAL})."
            )

        all_questions = basic_questions + specific_questions
        random.shuffle(all_questions)

        quiz = Quiz.objects.create(
            user=user,
            quiz_type=Quiz.SIMULATED,
            status=Quiz.IN_PROGRESS,
            quantity=len(all_questions),
        )

        QuizQuestion.objects.bulk_create(
            [
                QuizQuestion(quiz=quiz, question=q, order=i + 1)
                for i, q in enumerate(all_questions)
            ]
        )

        return quiz

    @staticmethod
    def get_subject_breakdown(quiz: Quiz) -> list[dict]:
        """Retorna o desempenho por disciplina de um simulado finalizado."""
        rows = (
            UserAnswer.objects.filter(quiz=quiz)
            .values("question__subject__name", "question__subject__color")
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
            .order_by("question__subject__name")
        )

        return [
            {
                "name": row["question__subject__name"],
                "color": row["question__subject__color"],
                "total": row["total"],
                "correct": row["correct"],
                "percentage": round(row["correct"] / row["total"] * 100)
                if row["total"]
                else 0,
            }
            for row in rows
        ]
