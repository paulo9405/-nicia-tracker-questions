"""
QuizService — criação e gestão de sessões de treino.

Regras de negócio:
- Um quiz só aceita respostas se estiver IN_PROGRESS.
- Cada questão só pode ser respondida uma vez por quiz (UNIQUE constraint).
- Questões não respondidas contam como erradas (selected_alternative=None).
- is_correct é calculado e persistido no momento do submit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone as tz

from apps.exams.models import Quiz, QuizQuestion, UserAnswer
from apps.questions.models import Alternative, Subject, Topic
from apps.questions.services.question_service import QuestionService


@dataclass
class QuizResult:
    quiz: Quiz
    total: int
    correct: int
    wrong: int
    skipped: int
    percentage: float
    items: list = field(default_factory=list)


class QuizService:

    # ------------------------------------------------------------------ #
    # Criação                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def create_practice_quiz(
        user,
        subject_id: str,
        topic_id: str | None,
        quantity: int,
    ) -> Quiz:
        subject = Subject.objects.get(pk=subject_id)
        topic = Topic.objects.get(pk=topic_id) if topic_id else None

        questions = list(
            QuestionService.get_practice_questions(subject_id, topic_id, quantity)
        )

        quiz = Quiz.objects.create(
            user=user,
            subject=subject,
            topic=topic,
            quiz_type=Quiz.PRACTICE,
            status=Quiz.IN_PROGRESS,
            quantity=len(questions),
        )

        QuizQuestion.objects.bulk_create(
            [
                QuizQuestion(quiz=quiz, question=q, order=i + 1)
                for i, q in enumerate(questions)
            ]
        )

        return quiz

    # ------------------------------------------------------------------ #
    # Submit                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def submit_answers(quiz: Quiz, raw_answers: dict[str, str]) -> Quiz:
        """
        raw_answers: {str(question_id): str(alternative_id)}
        Questões sem entrada no dict contam como puladas (is_correct=False).
        """
        if quiz.is_finished:
            return quiz

        quiz_questions = list(
            QuizQuestion.objects.filter(quiz=quiz).select_related("question")
        )

        # Pré-carrega todas as alternativas das questões do quiz numa única
        # query, em vez de uma query por questão respondida (evita N+1).
        question_ids = [qq.question_id for qq in quiz_questions]
        alternatives_by_id = {
            str(alt.id): alt
            for alt in Alternative.objects.filter(question_id__in=question_ids)
        }

        answers_to_create = []
        for qq in quiz_questions:
            alt_id = raw_answers.get(str(qq.question_id))
            selected_alt = None
            is_correct = False

            if alt_id:
                alt = alternatives_by_id.get(str(alt_id))
                # Valida que a alternativa pertence à questão respondida —
                # impede submeter o id de uma alternativa de outra questão.
                if alt is not None and alt.question_id == qq.question_id:
                    selected_alt = alt
                    is_correct = alt.is_correct

            answers_to_create.append(
                UserAnswer(
                    quiz=quiz,
                    question=qq.question,
                    selected_alternative=selected_alt,
                    is_correct=is_correct,
                )
            )

        UserAnswer.objects.bulk_create(answers_to_create)

        quiz.status = Quiz.FINISHED
        quiz.finished_at = tz.now()
        quiz.save(update_fields=["status", "finished_at"])

        return quiz

    # ------------------------------------------------------------------ #
    # Resultado                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_result(quiz: Quiz) -> QuizResult:
        quiz_questions = (
            QuizQuestion.objects.filter(quiz=quiz)
            .select_related("question__subject")
            .prefetch_related("question__alternatives")
            .order_by("order")
        )

        answers_by_qid = {
            ua.question_id: ua
            for ua in UserAnswer.objects.filter(quiz=quiz).select_related(
                "selected_alternative"
            )
        }

        items = []
        for qq in quiz_questions:
            ua = answers_by_qid.get(qq.question_id)
            items.append(
                {
                    "order": qq.order,
                    "question": qq.question,
                    "alternatives": qq.question.alternatives.all(),
                    "selected": ua.selected_alternative if ua else None,
                    "is_correct": ua.is_correct if ua else False,
                    "is_skipped": ua is None or ua.selected_alternative is None,
                }
            )

        total = len(items)
        correct = sum(1 for i in items if i["is_correct"])
        skipped = sum(1 for i in items if i["is_skipped"])
        wrong = total - correct - skipped
        percentage = round(correct / total * 100, 1) if total > 0 else 0.0

        return QuizResult(
            quiz=quiz,
            total=total,
            correct=correct,
            wrong=wrong,
            skipped=skipped,
            percentage=percentage,
            items=items,
        )
