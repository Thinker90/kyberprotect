from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Lesson, Task, Achievement,
    UserAchievement, Notification, News,
    Test, Question, Answer, UserTest
)


# Админка для управления пользовательскими данными
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'is_active', 'is_staff', 'notify_by_email')
    list_filter = ('is_staff', 'is_superuser', 'notify_by_email')
    search_fields = ('username', 'email')
    # Добавляем дополнительные поля в форму редактирования пользователя
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('avatar', 'notify_by_email', 'progress')}),
    )


# Админка для лекций
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)


# Админка для задач, связанных с лекциями
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'question', 'points')
    search_fields = ('question',)
    list_filter = ('lesson',)


# Админка для достижений
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'condition')
    search_fields = ('title', 'condition')


# Админка для достижений, полученных пользователями
@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__title')
    list_filter = ('earned_at',)


# Админка для уведомлений пользователям
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')


# Админка для новостей
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('created_at', 'is_published')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)


# Админка для тестов, связанных с лекциями
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)


# Админка для вопросов к тестам
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'question_text', 'question_type')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
    ordering = ('-test',)


# Админка для вариантов ответов на вопросы
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer_text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('answer_text',)
    ordering = ('-question',)


# Админка для отслеживания прохождения тестов пользователями
@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'test__title')
    ordering = ('-completed_at',)
