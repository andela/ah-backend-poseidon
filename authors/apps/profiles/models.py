from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..authentication.models import User


class Profile(models.Model):

    "This creates user profiles."
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.URLField(null=True)
    following = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# This signals the `Profile` model when a user has been registered
# for their profile to be created.
@receiver(post_save, sender=User)
def create_related_profile(*args, **kwargs):
    instance = kwargs['instance']

    if instance and kwargs['created']:
        instance.profile = Profile.objects.create(user=instance)
