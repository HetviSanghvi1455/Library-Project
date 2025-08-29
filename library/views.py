from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from SmartLibProject.settings import BASE_DIR
from .models import Book, Rating, Issue, Genre, Notification
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Avg
from django.http import JsonResponse, HttpResponse, FileResponse
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.contrib import messages
from django.conf.urls.static import static
from django.utils import timezone
from .forms import CustomUserCreationForm

# Home page

def home(request):
    return render(request, 'library/home.html')

# Signup

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'library/signup.html', {'form': form})

# Login

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})

# Staff-only login (strict credential pair: username 'hetvi' and password '123456789')
def staff_login_view(request):
    # Always force fresh login prompt
    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)
    next_url = request.GET.get('next') or request.POST.get('next') or 'manage_books'
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.username != 'hetvi':
                messages.error(request, 'Invalid staff credentials.')
            else:
                login(request, user)
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid staff credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'library/staff_login.html', {'form': form, 'next': next_url})

# Logout

def logout_view(request):
    logout(request)
    return redirect('home')

def admin_portal(request):
    logout(request)
    from django.shortcuts import redirect as _redirect
    return _redirect('/admin/login/?next=/admin/')

# Dashboard
@login_required
def dashboard(request):
    book_count = Book.objects.count()
    
    # Get user's issued books
    issued_books = Issue.objects.filter(user=request.user, status='issued')
    
    # Get available books (not currently issued)
    # This query is more efficient as it avoids N+1 lookups from the `is_available` property.
    # It now shows up to 12 books. You can change this number or remove the limit `[:12]`
    # if you want to show all available books on the dashboard.
    available_books = Book.objects.exclude(issue__status='issued')[:20]
    
    # Get overdue books
    overdue_books = issued_books.filter(due_date__lt=datetime.now())
    
    # Unread notifications count
    unread_notifications = request.user.notifications.filter(is_read=False).count()

    context = {
        'book_count': book_count,
        'issued_books': issued_books,
        'available_books': available_books,
        'overdue_books': overdue_books,
        'total_issued': issued_books.count(),
        'total_overdue': overdue_books.count(),
        'unread_notifications': unread_notifications,
    }
    return render(request, 'library/dashboard.html', context)

# Book List
@login_required
def book_list(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Genre filtering
    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        books = books.filter(genre__id=genre_filter)
    
    # Add user rating and average rating to each book
    for book in books:
        user_rating = Rating.objects.filter(user=request.user, book=book).first()
        book.user_rating = user_rating.score if user_rating else 0
    
    context = {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'selected_genre': genre_filter,
    }
    return render(request, 'library/book_list.html', context)

# Staff-only view reusing book list for management entry
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_books(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        books = books.filter(genre__id=genre_filter)
    for book in books:
        user_rating = Rating.objects.filter(user=request.user, book=book).first()
        book.user_rating = user_rating.score if user_rating else 0
    context = {
        'books': books,
        'genres': genres,
        'search_query': search_query,
        'selected_genre': genre_filter,
    }
    return render(request, 'library/book_list.html', context)

# Add Book
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_book(request):
    genres = Genre.objects.all()
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        description = request.POST.get('description', '')
        pdf = request.FILES['pdf']
        # get genre from POST data
        genre_id = request.POST.get('genre')
        genre = Genre.objects.get(id=genre_id) if genre_id else None
        poster = request.FILES.get('poster')
        Book.objects.create(
            title=title, author=author, description=description, pdf=pdf, genre=genre, poster=poster
        )
        return redirect('book_list')
    return render(request, 'library/add_book.html', {'genres': genres})

# Edit Book
@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    genres = Genre.objects.all()
    if request.method == 'POST':
        # handle form submission, including updating the genre
        genre_id = request.POST.get('genre')
        book.genre = Genre.objects.get(id=genre_id) if genre_id else None
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.description = request.POST.get('description', '')
        if 'pdf' in request.FILES:
            book.pdf = request.FILES['pdf']
        if 'poster' in request.FILES:
            book.poster = request.FILES['poster']
        book.save()
        return redirect('book_list')
    return render(request, 'library/edit_book.html', {'book': book, 'genres': genres})

# Delete Book
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/delete_book.html', {'book': book})

# Rate Book
@login_required
@csrf_exempt
def rate_book(request, book_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        rating_value = int(data.get('rating', 0))
        book = get_object_or_404(Book, id=book_id)
        rating, created = Rating.objects.get_or_create(user=request.user, book=book)
        rating.score = rating_value
        rating.save()
        return JsonResponse({'success': True, 'message': 'Rating saved!'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# Issue Book
@login_required
def issue_book(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)
        if book.is_available:
            issue = Issue.objects.create(
                user=request.user,
                book=book,
                due_date=datetime.now() + timedelta(days=14)
            )
            # Create in-app notification
            Notification.objects.create(
                user=request.user,
                title='Book Issued',
                message=f"You issued '{book.title}' by {book.author}. Due on {issue.due_date.strftime('%b %d, %Y')}.",
                level='success',
                link_url='/dashboard/'
            )
            return JsonResponse({'success': True, 'message': 'Book issued successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'Book is not available'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# Return Book
@login_required
def return_book(request, issue_id):
    if request.method == 'POST':
        try:
            issue = Issue.objects.get(id=issue_id, user=request.user)
            issue.status = 'returned'
            issue.return_date = timezone.now()
            issue.save()
            # Create in-app notification
            Notification.objects.create(
                user=request.user,
                title='Book Returned',
                message=f"You returned '{issue.book.title}'. Thanks!",
                level='info',
                link_url='/dashboard/'
            )
            return JsonResponse({'success': True, 'message': 'Book returned successfully!'})
        except Issue.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Issue not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'library/notifications.html', {'notifications': notifications})

@login_required
def notifications_mark_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# Get Recommendations
@login_required
def get_recommendations(request):
    # Simple collaborative filtering
    user_ratings = Rating.objects.filter(user=request.user)
    if user_ratings.count() < 2:
        # If user hasn't rated enough books, show popular books
        popular_books = Book.objects.annotate(
            avg_rating=Avg('rating__score')
        ).order_by('-avg_rating')[:5]
        return render(request, 'library/recommendations.html', {
            'recommendations': popular_books,
            'type': 'popular'
        })
    
    # Get similar users
    user_ratings_dict = {r.book.id: r.score for r in user_ratings}
    all_ratings = Rating.objects.exclude(user=request.user)
    
    # Find users with similar tastes
    similar_users = defaultdict(list)
    for rating in all_ratings:
        if rating.book.id in user_ratings_dict:
            # Calculate similarity based on rating difference
            similarity = 5 - abs(rating.score - user_ratings_dict[rating.book.id])
            similar_users[rating.user.id].append(similarity)
    
    # Get average similarity for each user
    user_similarities = {}
    for user_id, similarities in similar_users.items():
        if len(similarities) >= 2:  # At least 2 books in common
            user_similarities[user_id] = np.mean(similarities)
    
    # Get recommendations from similar users
    recommended_books = set()
    for user_id, similarity in sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:3]:
        user_ratings = Rating.objects.filter(user_id=user_id)
        for rating in user_ratings:
            if rating.book.id not in user_ratings_dict and rating.score >= 4:
                recommended_books.add(rating.book.id)
    
    recommendations = Book.objects.filter(id__in=recommended_books)
    if not recommendations.exists():
        # Fallback to popular books if no personalized recommendations
        popular_books = Book.objects.annotate(
            avg_rating=Avg('rating__score')
        ).order_by('-avg_rating')[:5]
        return render(request, 'library/recommendations.html', {
            'recommendations': popular_books,
            'type': 'popular'
        })
    return render(request, 'library/recommendations.html', {
        'recommendations': recommendations,
        'type': 'personalized'
    })

@login_required
def view_pdf(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not book.pdf:
        from django.http import Http404
        raise Http404("PDF not found.")
    return FileResponse(book.pdf.open('rb'), content_type='application/pdf')

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# urlpatterns = [
#     # ...your patterns...
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
