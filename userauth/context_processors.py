from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_seen=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}

from .models import DirectMessage

def unread_message_count(request):
    if request.user.is_authenticated:
        count = DirectMessage.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}