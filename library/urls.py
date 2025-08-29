from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('manage/books/', views.manage_books, name='manage_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('rate_book/<int:book_id>/', views.rate_book, name='rate_book'),
    path('books/<int:book_id>/issue/', views.issue_book, name='issue_book'),
    path('issues/<int:issue_id>/return/', views.return_book, name='return_book'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('books/<int:book_id>/view/', views.view_pdf, name='view_pdf'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/mark_read/', views.notifications_mark_read, name='notifications_mark_read'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
