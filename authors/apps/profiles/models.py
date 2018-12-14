from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..article.models import Article
from ..authentication.models import User
from ..comments.models import Comment


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


class Notification(models.Model):
    """
    Notification class handles creation
    and sending of notifications to users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    body = models.CharField(max_length=200)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.type

    # notification for creation of article by author user follows
    @receiver(post_save, sender=Article)
    def create_notification(*args, **kwargs):
        user = kwargs['instance'].author
        for i in user.profile.followers():
            follower = User.objects.get(pk=i.user_id)
            title = 'create article'
            body = 'article has been created by ' + user.username
            notify = Notification(user=follower, type=title, body=body)
            notify.save()

    # notification for comment on article favouriated.
    @receiver(post_save, sender=Comment)
    def create_notification_comment(*args, **kwargs):
        article_slug = kwargs['instance'].slug_id
        article = Article.objects.get(slug=article_slug)
        for i in article.is_favourite_by():
            user = User.objects.get(username=i)
            title = 'new comment on '
            body = 'user has posted new comment'
            notify = Notification(user=user, type=title, body=body)
            notify.save()
