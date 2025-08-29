from django.contrib import admin
from .models import Book, Rating, Issue, Genre, Notification

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'uploaded_at', 'is_available']
    list_filter = ['genre', 'uploaded_at']
    search_fields = ['title', 'author', 'description']
    date_hierarchy = 'uploaded_at'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'score')  # use 'score' instead of 'rating'
    list_filter = ('score',)  # use 'score' instead of 'rating'

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'status', 'issue_date', 'due_date', 'is_overdue']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['user__username', 'book__title']
    date_hierarchy = 'issue_date'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'level', 'is_read', 'created_at']
    list_filter = ['level', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
