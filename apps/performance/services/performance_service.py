from dataclasses import dataclass

from django.db.models import Count, Q

from apps.exams.models import UserAnswer

MIN_QUESTIONS_FOR_RANKING = 3


@dataclass
class SubjectPerformance:
    subject_id: str
    name: str
    slug: str
    color: str
    category: str
    total: int
    correct: int
    percentage: int


@dataclass
class TopicPerformance:
    name: str
    subject_name: str
    subject_color: str
    total: int
    correct: int
    percentage: int


@dataclass
class PerformanceStats:
    subjects: list  # list[SubjectPerformance], sorted weakest first
    weak_topics: list  # list[TopicPerformance], bottom 5
    strong_topics: list  # list[TopicPerformance], top 5
    total_subjects_studied: int
    total_topics_studied: int
    has_topic_data: bool


class PerformanceService:
    @staticmethod
    def get_full_stats(user) -> PerformanceStats:
        subject_rows = (
            UserAnswer.objects.filter(quiz__user=user)
            .values(
                "question__subject__id",
                "question__subject__name",
                "question__subject__slug",
                "question__subject__color",
                "question__subject__category",
            )
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
        )

        subjects = sorted(
            [
                SubjectPerformance(
                    subject_id=str(row["question__subject__id"]),
                    name=row["question__subject__name"],
                    slug=row["question__subject__slug"],
                    color=row["question__subject__color"],
                    category=row["question__subject__category"],
                    total=row["total"],
                    correct=row["correct"],
                    percentage=(
                        round(row["correct"] / row["total"] * 100)
                        if row["total"]
                        else 0
                    ),
                )
                for row in subject_rows
            ],
            key=lambda s: s.percentage,
        )

        topic_rows = (
            UserAnswer.objects.filter(
                quiz__user=user,
                question__topic__isnull=False,
            )
            .values(
                "question__topic__name",
                "question__subject__name",
                "question__subject__color",
            )
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
        )

        all_topics = [
            TopicPerformance(
                name=row["question__topic__name"],
                subject_name=row["question__subject__name"],
                subject_color=row["question__subject__color"],
                total=row["total"],
                correct=row["correct"],
                percentage=(
                    round(row["correct"] / row["total"] * 100) if row["total"] else 0
                ),
            )
            for row in topic_rows
        ]

        # Apenas tópicos com volume mínimo entram no ranking
        qualified = sorted(
            [t for t in all_topics if t.total >= MIN_QUESTIONS_FOR_RANKING],
            key=lambda t: t.percentage,
        )
        weak_topics = qualified[:5]
        strong_topics = list(reversed(qualified))[:5]

        return PerformanceStats(
            subjects=subjects,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            total_subjects_studied=len(subjects),
            total_topics_studied=len(all_topics),
            has_topic_data=bool(all_topics),
        )
