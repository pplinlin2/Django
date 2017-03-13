from django.contrib import admin

from . import models


class TextInline(admin.StackedInline):
    model = models.Text


class QuizInline(admin.StackedInline):
    model = models.Quiz


class AnswerInline(admin.StackedInline):
    model = models.Answer

    
class CourseAdmin(admin.ModelAdmin):
    inlines = [TextInline, QuizInline]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline,]

admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Text)
admin.site.register(models.Quiz)
admin.site.register(models.MultipleChoiceQuestion, QuestionAdmin)
admin.site.register(models.TrueFalseQuestion, QuestionAdmin)
