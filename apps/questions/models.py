from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class Subject(BaseModel):
    BASIC = "basic"
    SPECIFIC = "specific"
    CATEGORY_CHOICES = [(BASIC, "Básica"), (SPECIFIC, "Específica")]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default=SPECIFIC
    )
    color = models.CharField(max_length=7, default="#6c757d")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Topic(BaseModel):
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="topics"
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("subject", "slug")]
        verbose_name = "Tópico"
        verbose_name_plural = "Tópicos"

    def __str__(self):
        return f"{self.subject.name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Question(BaseModel):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DIFFICULTY_CHOICES = [(EASY, "Fácil"), (MEDIUM, "Médio"), (HARD, "Difícil")]

    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="questions"
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.PROTECT, related_name="questions", null=True, blank=True
    )
    external_id = models.SlugField(max_length=50, unique=True, blank=True)
    content_hash = models.CharField(max_length=64, blank=True)
    text = models.TextField()
    context_text = models.TextField(blank=True, null=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    board = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default=MEDIUM
    )
    explanation = models.TextField(blank=True)
    source = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["subject", "external_id"]
        verbose_name = "Questão"
        verbose_name_plural = "Questões"
        indexes = [
            models.Index(fields=["subject", "topic", "difficulty", "is_active"]),
            models.Index(fields=["board", "year"]),
        ]

    def __str__(self):
        return f"[{self.subject}] {self.text[:60]}..."


class Alternative(BaseModel):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    LETTER_CHOICES = [(A, "A"), (B, "B"), (C, "C"), (D, "D"), (E, "E")]

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="alternatives"
    )
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["letter"]
        unique_together = [("question", "letter")]
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

    def __str__(self):
        return f"{self.letter}) {self.text[:50]}"
