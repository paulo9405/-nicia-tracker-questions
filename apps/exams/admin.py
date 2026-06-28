from django.contrib import admin

from .models import Quiz, QuizQuestion, UserAnswer


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    raw_id_fields = ("question",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "quiz_type", "status", "quantity", "started_at")
    list_filter = ("quiz_type", "status")
    search_fields = ("user__email",)
    date_hierarchy = "started_at"
    inlines = [QuizQuestionInline]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "quiz", "question", "is_correct", "answered_at")
    list_filter = ("is_correct",)
    search_fields = ("quiz__user__email",)
