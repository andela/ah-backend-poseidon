from .exceptions import NotificationDoesNotExist, NotificaionForbidden
from .models import Notification, Profile


def return_notification(request, notification_id):
        try:
            query = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            raise NotificationDoesNotExist

        if not query.user_id == request.user.pk:
            raise NotificaionForbidden
        return query
