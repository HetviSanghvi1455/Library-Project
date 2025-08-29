from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color for UI
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    pdf = models.FileField(upload_to='books/pdfs/', blank=True, null=True)
    poster = models.ImageField(upload_to='books/posters/', blank=True, null=True)  # Add this line
    uploaded_at = models.DateTimeField(auto_now_add=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        """Check if book is available for issuing"""
        return not self.issue_set.filter(status='issued').exists()
    
    @property
    def average_rating(self):
        """Calculate average rating for the book"""
        avg = self.rating_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'book')
    
    def __str__(self):
        return f"{self.user.username} rated {self.book.title} as {self.score}"

class Issue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='issued')

    def __str__(self):
        return f"{self.user.username} issued {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the book is overdue"""
        if self.status == 'issued' and self.due_date < timezone.now():
            return True
        return False


class Notification(models.Model):
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    link_url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"