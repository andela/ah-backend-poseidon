from rest_framework import viewsets, status

# Create your views here.
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authors.apps.article.json_renderer import ArticleJSONRenderer
from authors.apps.article.models import Article
from authors.apps.article.serializers import ArticleSerializer


class ArticleViewSet(viewsets.ViewSet):
    """
    Article ViewSet
    Handles all CRUD operations
    """
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def create(self, request):
        """
        creates an article
        :param request:
        :return:
        """
        article = request.data.get("article", {})
        article.update({"author": 1})  # request.user.pk
        serializer = self.serializer_class(data=article,)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        returns a list of all articles
        :param request:
        :return:
        """
        queryset = Article.objects.all()
        serializer = ArticleSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug=None):
        """
        returns a specific article based on the slug
        :param slug:
        :param request:
        :return:
        """
        queryset = Article.objects.all()
        article = get_object_or_404(queryset, slug=slug)

        serializer = self.serializer_class(
            article, context={'request': request})
        return Response(serializer.data)




