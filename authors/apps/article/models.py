"""
module to define the structure of the article
"""

from django.db import models
from django.db.models import Avg
from taggit.managers import TaggableManager

from authors.apps.article.utils import generate_slug
from authors.apps.authentication.models import User


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
        return float('%.2f' % (ratings["score"]
                               if ratings['score'] else 0))

    def is_favourite_by(self):
        return self.favourite_by.all()

    class Meta:
        get_latest_by = 'created_on'
        ordering = ['-created_on', 'author']


class Rating(models.Model):
    """
    Model for rating an article
    """
    article = models.ForeignKey(
        Article,
        related_name="scores",
        on_delete=models.CASCADE)
    rated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="scores",
        null=True)
    rated_on = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["-score"]
