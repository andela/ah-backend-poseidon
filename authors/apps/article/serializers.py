from datetime import datetime

from rest_framework import serializers

from authors.apps.article.exceptions import NotFoundException
from authors.apps.article.models import Article
from authors.apps.authentication.models import User


class ArticleSerializer(serializers.ModelSerializer):
    """
    class to serialize the article models
    """

    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False)
    slug = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        article = Article.objects.create(**validated_data)
        return article

    class Meta:
        """
        class behaviours
        """
        model = Article
        fields = '__all__'

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
            raise NotFoundException("You don't own update permissions for this Article, Sorry!")

        required = {"title", "description", "body"}
        keys = set(data.keys())

        missing = required.difference(keys)

        for val in missing:
            data.update({val: article.__getattribute__(val)})

        data.update({
            "author": user.pk,
            "updated_at": datetime.now()
        })
        return article, data
