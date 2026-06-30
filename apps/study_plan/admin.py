from django.contrib import admin

from .models import ActiveLearningNote, ErrorNotebookEntry, GuidedReflection, LessonProgress, StudyChapter, StudyModule


class StudyChapterInline(admin.TabularInline):
    model = StudyChapter
    extra = 0
    fields = ("order", "title", "estimated_minutes", "tags", "is_active")
    ordering = ("order",)


@admin.register(StudyModule)
class StudyModuleAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "category", "study_phase", "estimated_hours", "chapter_count", "is_active")
    list_filter = ("category", "study_phase", "is_active")
    search_fields = ("title", "master_file")
    ordering = ("order",)
    inlines = [StudyChapterInline]


@admin.register(StudyChapter)
class StudyChapterAdmin(admin.ModelAdmin):
    list_display = ("module", "order", "title", "estimated_minutes", "is_active")
    list_filter = ("module", "is_active")
    search_fields = ("title", "tags")
    ordering = ("module__order", "order")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "chapter", "status", "completed_at")
    list_filter = ("status",)
    search_fields = ("user__email",)


@admin.register(ActiveLearningNote)
class ActiveLearningNoteAdmin(admin.ModelAdmin):
    list_display = ("user", "chapter", "created_at", "updated_at")
    search_fields = ("user__email", "chapter__title")
    raw_id_fields = ("chapter",)


@admin.register(GuidedReflection)
class GuidedReflectionAdmin(admin.ModelAdmin):
    list_display = ("user", "chapter", "created_at", "updated_at")
    search_fields = ("user__email", "chapter__title")
    raw_id_fields = ("chapter",)


@admin.register(ErrorNotebookEntry)
class ErrorNotebookEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "wrong_count", "last_wrong_at", "next_review_at", "is_reviewed")
    list_filter = ("is_reviewed", "question__subject")
    search_fields = ("user__email", "question__statement")
    raw_id_fields = ("question", "last_user_answer")
