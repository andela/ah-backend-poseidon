"""
module to define the structure of the article
"""

from django.db import models
from django.db.models import Avg
from taggit.managers import TaggableManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

from authors.apps.article.utils import generate_slug
from authors.apps.authentication.models import User


class LikeDislikeManager(models.Manager):
    # Gets all the votes greater than 0. In this case they're likes.
    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    # Gets all the votes less than 0. In this case they're dislikes.
    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)


class LikeDislike(models.Model):
    "Likes and Dislikes model."
    LIKE = 1
    DISLIKE = -1

    VOTES = ((DISLIKE, 'Dislike'), (LIKE, 'Like'))

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()


class Article(models.Model):
    """
    class to define the model of an article
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles", null=True)

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        error_messages={"required": "Add a title for your article."})

    description = models.TextField(
        null=False,
        blank=False,
        error_messages={"required": "Add a description for your article."})

    body = models.TextField(
        null=False,
        blank=False,
        error_messages={"required": "Add a body for your article."})

    user_rating = models.CharField(max_length=10, default='0')
    # auto_now_add sets the timezone.now when an instance is created
    created_on = models.DateTimeField(auto_now_add=True)
    # auto_now updates the field every time the save method is called
    updated_on = models.DateTimeField(auto_now=True)
    image_url = models.CharField(max_length=255, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    tags = TaggableManager(blank=True)
    favourites_count = models.IntegerField(default=0)
    view_counts = models.IntegerField(default=0)
    # bookmarks field is a manytomany descriptor for articles to users.
    bookmarks = models.ManyToManyField(
        'authentication.User', related_name="bookmark_article")
    votes = GenericRelation(LikeDislike, related_query_name='articles')

    def __str__(self):
        """
        :return: string
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        override default save() to generate slug
        :param args:
        :param kwargs:
        """
        self.slug = generate_slug(Article, self)

        super(Article, self).save(*args, **kwargs)

    @property
    def average_rating(self):
        """
        method to calculate the average rating of the article.
        """
        ratings = self.scores.all().aggregate(score=Avg("score"))
        return float('%.2f' % (ratings["score"] if ratings['score'] else 0))

    def is_favourite_by(self):
        return self.favourite_by.all()

    def bookmark(self, user):
        """bookmark article"""
        self.bookmarks.add(user)

    def unbookmark(self, user):
        """unbookmark article"""
        self.bookmarks.remove(user)

    def is_bookmarked(self, user):
        """check for bookmarked article"""
        return self.bookmarks.filter(id=user.pk).exists()

    class Meta:
        get_latest_by = 'created_on'
        ordering = ['-created_on', 'author']


class Rating(models.Model):
    """
    Model for rating an article
    """
    article = models.ForeignKey(
        Article, related_name="scores", on_delete=models.CASCADE)
    rated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scores", null=True)
    rated_on = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["-score"]


class Report(models.Model):
    """
    Model for reporting article
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)
    violation = models.BooleanField(default=False)
    action = models.BooleanField(default=False)
    message = models.CharField(max_length=200)
    create_at = models.DateTimeField(auto_now_add=True)
