from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import BaseModel
from apps.questions.models import Question, Subject


class StudyModule(BaseModel):
    PHASE_1 = "1"
    PHASE_2 = "2"
    PHASE_3 = "3"
    PHASE_4 = "4"
    PHASE_CHOICES = [
        (PHASE_1, "Fase 1 — Leitura"),
        (PHASE_2, "Fase 2 — Consolidação"),
        (PHASE_3, "Fase 3 — Treino de Prova"),
        (PHASE_4, "Fase 4 — Reta Final"),
    ]

    subject = models.OneToOneField(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_module",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    order = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    master_file = models.CharField(max_length=80)
    study_phase = models.CharField(max_length=1, choices=PHASE_CHOICES, default=PHASE_1)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    category = models.CharField(
        max_length=10,
        choices=[("specific", "Específica"), ("basic", "Básica")],
        default="specific",
    )
    icon = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Módulo de Estudo"
        verbose_name_plural = "Módulos de Estudo"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["category"]),
            models.Index(fields=["study_phase"]),
        ]

    def __str__(self):
        return f"[M{self.order}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def chapter_count(self):
        return self.chapters.filter(is_active=True).count()


class StudyChapter(BaseModel):
    module = models.ForeignKey(
        StudyModule, on_delete=models.CASCADE, related_name="chapters"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    order = models.PositiveSmallIntegerField()
    content = models.TextField(blank=True)
    key_points = models.TextField(blank=True)
    estimated_minutes = models.PositiveSmallIntegerField(default=30)
    tags = models.JSONField(default=list, blank=True)
    related_subjects = models.ManyToManyField(
        Subject, blank=True, related_name="study_chapters"
    )
    sections_source = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        unique_together = [("module", "slug"), ("module", "order")]
        verbose_name = "Capítulo"
        verbose_name_plural = "Capítulos"
        indexes = [
            models.Index(fields=["module", "order"]),
            models.Index(fields=["module", "is_active"]),
        ]

    def __str__(self):
        return f"[{self.module.title}] Cap. {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class LessonProgress(BaseModel):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (NOT_STARTED, "Não iniciado"),
        (IN_PROGRESS, "Em andamento"),
        (COMPLETED, "Concluído"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
    )
    chapter = models.ForeignKey(
        StudyChapter, on_delete=models.CASCADE, related_name="progresses"
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=NOT_STARTED
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [("user", "chapter")]
        verbose_name = "Progresso de Lição"
        verbose_name_plural = "Progressos de Lição"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "completed_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.chapter} [{self.status}]"

    @property
    def is_completed(self):
        return self.status == self.COMPLETED


class ActiveLearningNote(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="active_learning_notes",
    )
    chapter = models.ForeignKey(
        StudyChapter, on_delete=models.CASCADE, related_name="notes"
    )
    explanation = models.TextField()

    class Meta:
        unique_together = [("user", "chapter")]
        verbose_name = "Nota de Aprendizagem Ativa"
        verbose_name_plural = "Notas de Aprendizagem Ativa"
        indexes = [
            models.Index(fields=["user", "chapter"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.chapter} [nota]"


class GuidedReflection(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guided_reflections",
    )
    chapter = models.ForeignKey(
        StudyChapter, on_delete=models.CASCADE, related_name="reflections"
    )
    what_understood = models.TextField()
    most_important = models.TextField()
    most_difficult = models.TextField()

    class Meta:
        unique_together = [("user", "chapter")]
        verbose_name = "Reflexão Guiada"
        verbose_name_plural = "Reflexões Guiadas"
        indexes = [
            models.Index(fields=["user", "chapter"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.chapter} [reflexão]"


def _next_review_date(wrong_count: int):
    from datetime import date, timedelta

    delays = {1: 1, 2: 3, 3: 7}
    days = delays.get(wrong_count, 14)
    return date.today() + timedelta(days=days)


class ErrorNotebookEntry(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="error_notebook_entries",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="error_notebook_entries",
    )
    last_user_answer = models.ForeignKey(
        "exams.UserAnswer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    wrong_count = models.PositiveSmallIntegerField(default=1)
    last_wrong_at = models.DateTimeField(default=timezone.now)
    next_review_at = models.DateField(null=True, blank=True)
    personal_note = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = [("user", "question")]
        verbose_name = "Entrada do Caderno de Erros"
        verbose_name_plural = "Entradas do Caderno de Erros"
        indexes = [
            models.Index(fields=["user", "next_review_at"]),
            models.Index(fields=["user", "wrong_count"]),
            models.Index(fields=["user", "is_reviewed"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.question_id} [erros: {self.wrong_count}]"
