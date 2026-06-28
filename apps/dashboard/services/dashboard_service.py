from dataclasses import dataclass
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.exams.models import Quiz, UserAnswer


@dataclass
class SubjectStat:
    name: str
    color: str
    total: int
    correct: int
    percentage: int


@dataclass
class DashboardStats:
    total_answered: int
    total_correct: int
    total_wrong: int
    total_quizzes: int
    streak: int
    overall_percentage: int
    subject_stats: list
    daily_goal: int
    today_answered: int
    today_remaining: int
    daily_goal_percentage: int
    recent_quizzes: list


class DashboardService:
    @staticmethod
    def get_stats(user) -> DashboardStats:
        totals = UserAnswer.objects.filter(quiz__user=user).aggregate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        )
        total_answered = totals["total"] or 0
        total_correct = totals["correct"] or 0
        total_wrong = total_answered - total_correct
        overall_pct = (
            round(total_correct / total_answered * 100) if total_answered else 0
        )

        total_quizzes = Quiz.objects.filter(user=user, status=Quiz.FINISHED).count()

        streak = DashboardService._compute_streak(user)

        subject_rows = (
            UserAnswer.objects.filter(quiz__user=user)
            .values("question__subject__name", "question__subject__color")
            .annotate(
                total=Count("id"),
                correct=Count("id", filter=Q(is_correct=True)),
            )
            .order_by("-total")
        )
        subject_stats = [
            SubjectStat(
                name=row["question__subject__name"],
                color=row["question__subject__color"],
                total=row["total"],
                correct=row["correct"],
                percentage=round(row["correct"] / row["total"] * 100)
                if row["total"]
                else 0,
            )
            for row in subject_rows
        ]

        today = timezone.localdate()
        today_answered = UserAnswer.objects.filter(
            quiz__user=user,
            answered_at__date=today,
        ).count()

        try:
            daily_goal = user.profile.daily_goal or 10
        except Exception:
            daily_goal = 10

        today_remaining = max(0, daily_goal - today_answered)
        daily_goal_pct = (
            min(round(today_answered / daily_goal * 100), 100) if daily_goal else 0
        )

        recent_quizzes = list(
            Quiz.objects.filter(user=user, status=Quiz.FINISHED)
            .select_related("subject")
            .annotate(
                correct_count=Count("answers", filter=Q(answers__is_correct=True)),
                wrong_count=Count("answers", filter=Q(answers__is_correct=False)),
            )
            .order_by("-finished_at")[:5]
        )

        return DashboardStats(
            total_answered=total_answered,
            total_correct=total_correct,
            total_wrong=total_wrong,
            total_quizzes=total_quizzes,
            streak=streak,
            overall_percentage=overall_pct,
            subject_stats=subject_stats,
            daily_goal=daily_goal,
            today_answered=today_answered,
            today_remaining=today_remaining,
            daily_goal_percentage=daily_goal_pct,
            recent_quizzes=recent_quizzes,
        )

    @staticmethod
    def _compute_streak(user) -> int:
        dates = list(
            Quiz.objects.filter(
                user=user, status=Quiz.FINISHED, finished_at__isnull=False
            )
            .dates("finished_at", "day")
            .order_by("-finished_at")
        )
        if not dates:
            return 0

        today = timezone.localdate()
        most_recent = dates[0]

        # Streak é válido apenas se o usuário estudou hoje ou ontem
        if (today - most_recent).days > 1:
            return 0

        streak = 0
        expected = most_recent
        for date in dates:
            if date == expected:
                streak += 1
                expected = expected - timedelta(days=1)
            else:
                break

        return streak
