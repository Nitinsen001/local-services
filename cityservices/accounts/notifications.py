from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify(user, message, notification_type, link=''):
    Notification.objects.create(
        recipient=user,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    if user.email:
        send_mail('Local Services Marketplace', message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)