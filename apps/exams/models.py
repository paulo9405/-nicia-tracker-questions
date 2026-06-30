from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.questions.models import Alternative, Question, Subject, Topic


class Quiz(BaseModel):
    PRACTICE = "practice"
    SIMULATED = "simulated"
    MINI = "mini"
    TYPE_CHOICES = [(PRACTICE, "Treino"), (SIMULATED, "Simulado"), (MINI, "Mini Quiz")]

    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    STATUS_CHOICES = [(IN_PROGRESS, "Em andamento"), (FINISHED, "Finalizado")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="quizzes", null=True, blank=True
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.PROTECT, related_name="quizzes", null=True, blank=True
    )
    quiz_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default=PRACTICE)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=IN_PROGRESS
    )
    chapter = models.ForeignKey(
        "study_plan.StudyChapter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mini_quizzes",
    )
    quantity = models.PositiveSmallIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "-started_at"]),
        ]

    def __str__(self):
        subject_name = self.subject.name if self.subject else "Geral"
        return f"[{self.get_quiz_type_display()}] {subject_name} — {self.quantity}q"

    @property
    def is_finished(self):
        return self.status == self.FINISHED


class QuizQuestion(BaseModel):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="quiz_questions"
    )
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, related_name="quiz_questions"
    )
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = [("quiz", "question"), ("quiz", "order")]
        verbose_name = "Questão do Quiz"
        verbose_name_plural = "Questões do Quiz"

    def __str__(self):
        return f"Quiz {self.quiz_id} — Q{self.order}"


class UserAnswer(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, related_name="user_answers"
    )
    selected_alternative = models.ForeignKey(
        Alternative, on_delete=models.PROTECT, null=True, blank=True
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("quiz", "question")]
        verbose_name = "Resposta"
        verbose_name_plural = "Respostas"
        indexes = [
            models.Index(fields=["quiz", "is_correct"]),
        ]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} Quiz {self.quiz_id}"
