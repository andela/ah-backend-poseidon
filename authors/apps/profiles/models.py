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
    follows = models.ManyToManyField(
        'self', related_name='followed_by', symmetrical=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    favourites = models.ManyToManyField(
        'article.Article',
        related_name='favourite_by')

    def __str__(self):
        return self.user.username

    # Adds a user to one's `followers` relation.
    def follow(self, profile):
        self.follows.add(profile)

    # Removes a user from one's `followers` relation.
    def unfollow(self, profile):
        self.follows.remove(profile)

    # Returns `True` if a user is following someone.
    def is_following(self, profile):
        return self.follows.filter(pk=profile.pk).exists()

    # Returns `True` if a user is followed by someone.
    def is_followed_by(self, profile):
        return self.followed_by.filter(pk=profile.pk).exists()

    # Returns one's followers.
    def followers(self):
        return self.followed_by.all()

    # Favourite an article
    def favourite(self, article):
        self.favourites.add(article)

    # method to not favourite article
    def not_favourite(self, article):
        self.favourites.remove(article)

    # check if user has an article selected as favourite
    def is_favourite(self, article):
        return self.favourites.filter(pk=article.pk).exists()


# This signals the `Profile` model when a user has been registered
# for their profile to be created.
@receiver(post_save, sender=User)
def create_related_profile(*args, **kwargs):
    instance = kwargs['instance']

    if instance and kwargs['created']:
        instance.profile = Profile.objects.create(user=instance)
