from django.contrib.auth.models import AnonymousUser


def unread_notifications(request):
    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return {"unread_notifications": 0}
    try:
        return {"unread_notifications": user.notifications.filter(is_read=False).count()}
    except Exception:
        return {"unread_notifications": 0}


