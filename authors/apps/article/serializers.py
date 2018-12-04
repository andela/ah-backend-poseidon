from rest_framework import serializers

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

