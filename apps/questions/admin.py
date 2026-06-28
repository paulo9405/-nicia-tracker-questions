from django.contrib import admin

from .models import Alternative, Question, Subject, Topic


class AlternativeInline(admin.TabularInline):
    model = Alternative
    extra = 0
    fields = ("letter", "text", "is_correct")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "color", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "is_active")
    list_filter = ("subject", "is_active")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "subject", "topic", "difficulty", "is_active")
    list_filter = ("subject", "difficulty", "is_active")
    search_fields = ("text", "external_id")
    inlines = [AlternativeInline]
    readonly_fields = ("external_id", "content_hash")

    @admin.display(description="Questão")
    def short_text(self, obj):
        return obj.text[:80]
