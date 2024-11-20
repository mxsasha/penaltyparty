from django.contrib import admin

from .models import Answer, Question, TestAttempt, TestGroup


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text", "status", "created", "modified")
    list_filter = ("status", "created", "modified")
    search_fields = ("question_text",)
    ordering = ("-created",)
    readonly_fields = ("created", "modified")
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "answer_text", "is_correct", "status", "created", "modified")
    list_filter = ("is_correct", "status", "created", "modified")
    search_fields = ("answer_text",)
    ordering = ("-created",)
    readonly_fields = ("created", "modified")


@admin.register(TestGroup)
class TestGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "group_name", "owner_email", "created", "modified")
    search_fields = ("token_owner", "token_test_taker", "owner_email")
    ordering = ("-created",)
    readonly_fields = ("token_owner", "token_test_taker", "created", "modified")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "participant_name", "test_group", "created", "modified")
    list_filter = ("test_group", "created", "modified")
    search_fields = ("token",)
    ordering = ("-created",)
    readonly_fields = ("token", "created", "modified")
