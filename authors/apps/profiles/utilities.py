from .exceptions import NotificationDoesNotExist, NotificaionForbidden
from .models import Notification, Profile
from django.dispatch import receiver
from ..comments.models import Comment, Article
from django.db.models.signals import post_save
from ..authentication.models import User


def return_notification(request, notification_id):
        try:
            query = Notification.objects.get(pk=notification_id)
        except Notification.DoesNotExist:
            raise NotificationDoesNotExist

        if not query.user_id == request.user.pk:
            raise NotificaionForbidden
        return query


def save_notification_db(follower, title, body):
    notify = Notification(user=follower, type=title, body=body)
    notify.save()


# notification for creation of article by author user follows
@receiver(post_save, sender=Article)
def create_notification(*args, **kwargs):
    user = kwargs['instance'].author
    body = 'article has been created by ' + user.username
    for i in user.profile.followers():
        follower = User.objects.get(pk=i.user_id)
        save_notification_db(follower, 'New article created', body)


# notification for comment on article favouriated.
@receiver(post_save, sender=Comment)
def create_notification_comment(*args, **kwargs):
    article_slug = kwargs['instance'].slug_id
    article = Article.objects.get(slug=article_slug)
    body = 'user has posted new comment'
    for i in article.is_favourite_by():
        user = User.objects.get(username=i)
        save_notification_db(user, 'new comment on favourated article', body)
