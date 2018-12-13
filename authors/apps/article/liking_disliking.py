from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    """
     Handles article likes data
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes',
        on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # This implements the liking logic
    def like(self, instance, user):
        like = instance.liking.filter(user=user.pk)
        dislike = instance.disliking.filter(user=user.pk)

        if not like.exists() and not dislike.exists():
            Like.objects.create(content_object=instance, user=user)

        elif like.exists() and not dislike.exists():
            like.delete()
        elif dislike.exists() and not like.exists():
            dislike.delete()
            Like.objects.create(content_object=instance, user=user)


class Dislike(models.Model):
    """
    Handels article dislikes data
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='dislikes',
        on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # This implements the disliking logic
    def dislike(self, instance, user):
        like = instance.liking.filter(user=user.pk)
        dislike = instance.disliking.filter(user=user.pk)

        if not dislike.exists() and not like.exists():
            Dislike.objects.create(content_object=instance, user=user)

        elif dislike.exists() and not like.exists():
            dislike.delete()
        elif like.exists() and not dislike.exists():
            like.delete()
            Dislike.objects.create(content_object=instance, user=user)
