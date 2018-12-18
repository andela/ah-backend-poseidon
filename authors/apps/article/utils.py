"""
Defines functions to do common tasks
"""
import math
from datetime import datetime

from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.response import Response


def generate_slug(article, self):
    """
    returns a slug
    :param self:
    :param article:
    :return:
    """
    if self.id:
        return self.slug

    new_slug = slugify(self.title)

    if article.objects.filter(slug=new_slug).count() > 0:
        size = math.floor(len(self.description.split()) / 2)
        new_slug = slugify(new_slug + " " +
                           " ".join(self.description.split()[:size]))

    if article.objects.filter(slug=new_slug).count() > 0:
        new_slug = slugify(new_slug + "-" + generate_unique_number())

    return new_slug


def generate_unique_number():
    """
    returns a unique number generated using the current date and time
    :return:
    """
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def bookmark_validator(article, request):
    """
    validator method for bookmarking article
    """
    user = request.user
    author = article.author
    bookmarked = article.is_bookmarked(user)
    if author == user:
        return Response({
            "message": "You can't bookmark your own article",
        },
                        status=status.HTTP_400_BAD_REQUEST)
    if bookmarked:
        return Response({
            "message": "Article already bookmarked by you",
        },
                        status=status.HTTP_400_BAD_REQUEST)
