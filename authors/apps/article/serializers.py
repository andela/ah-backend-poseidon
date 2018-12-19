"""
Module to handle app serializers
"""
from datetime import datetime

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from taggit_serializer.serializers import (TaggitSerializer,
                                           TagListSerializerField)

from authors.apps.article.exceptions import NotFoundException
from authors.apps.article.models import Article, Rating, Report
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    class to serialize the article models
    """

    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False)
    slug = serializers.CharField(read_only=True)
    user_rating = serializers.CharField(
        source="author.average_rating", required=False)
    tags = TagListSerializerField()
    favourites_count = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        """
        class behaviours
        """
        model = Article
        fields = ('slug', 'title', 'description', 'body', 'created_on',
                  'average_rating', 'user_rating', 'updated_on', 'image_url',
                  'author', 'tags', 'favourites_count', 'id',  'likes', 'dislikes')

    @staticmethod
    def validate_for_update(data: dict, user, slug):
        """
        :param data:
        :param user:
        :param slug:
        :return:
        """
        try:
            article = Article.objects.filter(
                slug__exact=slug, author__exact=user)
            if article.count() > 0:
                article = article[0]
            else:
                raise Article.DoesNotExist

        except Article.DoesNotExist:
            raise NotFoundException(
                "You don't own update permissions for this Article, Sorry!")

        required = {"title", "description", "body"}
        keys = set(data.keys())

        missing = required.difference(keys)

        for val in missing:
            data.update({val: article.__getattribute__(val)})

        data.update({"author": user.pk, "updated_at": datetime.now()})
        return article, data

    def to_representation(self, instance):
        """
        method formats serializer display response
        """
        response = super().to_representation(instance)
        profile = ProfileSerializer(
            Profile.objects.get(user=instance.author),
            context=self.context).data
        response['author'] = profile
        return response

    def get_favourites_count(self, instance):
        return instance.favourite_by.count()

    # Gets all the articles likes
    def get_likes(self, instance):
        return instance.votes.likes().count()

    # # Gets all the articles dislikes
    def get_dislikes(self, instance):
        return instance.votes.dislikes().count()


class RatingSerializer(serializers.ModelSerializer):
    """
    class holding logic for article rating
    """

    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all())
    rated_on = serializers.DateTimeField(read_only=True)
    rated_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    score = serializers.DecimalField(
        required=True, max_digits=5, decimal_places=2)

    @staticmethod
    def update_data(data, slug, user: User):
        """
        method to update the article with a rating
        """
        try:
            article = Article.objects.get(slug__exact=slug)
        except Article.DoesNotExist:
            raise NotFoundException("Article is not found.")

        if article.author == user:
            raise serializers.ValidationError({
                "article":
                ["Please rate an article that does not belong to you"]
            })

        score = data.get("score", 0)
        if score > 5 or score < 0:
            raise serializers.ValidationError({
                "score":
                ["Score value must not go "
                 "below `0` and not go beyond `5`"]
            })

        data.update({"article": article.pk})
        data.update({"rated_by": user.pk})
        return data

    def create(self, validated_data):
        """
        method to create and save a rating for
        """
        rated_by = validated_data.get("rated_by", None)
        article = validated_data.get("article", None)
        score = validated_data.get("score", 0)

        try:
            rating = Rating.objects.get(
                rated_by=rated_by, article__slug=article.slug)
        except Rating.DoesNotExist:
            return Rating.objects.create(**validated_data)

        rating.score = score
        rating.save()
        return rating

    def to_representation(self, instance):
        """
        method to format the display of serializers
        """
        response = super().to_representation(instance)

        response['article'] = instance.article.slug
        response['rated_by'] = instance.rated_by.username
        response['average_rating'] = instance.article.average_rating
        return response

    class Meta:
        """
        class behaviours
        """
        model = Rating
        fields = ("score", "rated_by", "rated_on", "article")


class PaginatedDataSerializer(PageNumberPagination):
    """
    Pagination class
    """

    def get_paginated_response(self, data):
        """
        Formats page responses to include page links
        """
        return {
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link()
            },
            "current_page": self.page.number,
            "results": data
        }


class ReportSerializer(serializers.ModelSerializer):
    """
    Report article class.
    """
    class Meta:
        model = Report
        fields = ("id", "article_id", "viewed", "action", "violation",
                  "message", "create_at")
