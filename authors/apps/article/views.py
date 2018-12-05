from rest_framework import viewsets, status

# Create your views here.
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authors.apps.article.exceptions import NotFoundException
from authors.apps.article.renderer import ArticleJSONRenderer
from authors.apps.article.models import Article
from authors.apps.article.serializers import ArticleSerializer


class ArticleViewSet(viewsets.ViewSet):
    """
    Article ViewSet
    Handles all CRUD operations
    """
    permission_classes = (IsAuthenticated,)
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
        article.update({"author": request.user.pk})  # request.user.pk
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

    def update(self, request, slug=None):
        """
        update a specific article
        :param request:
        :param slug:
        :return:
        """
        article_update = request.data.get("article", {})

        article, article_update = self.serializer_class.validate_for_update(
            article_update, request.user, slug)

        serializer = self.serializer_class(
            data=article_update, context={'request': request})
        serializer.instance = article
        serializer.is_valid(raise_exception=True)

        serializer.update(article, serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, slug=None):
        """
        delete an article
        :param request:
        :param slug:
        :return:
        """

        try:
            article = Article.objects.filter(
                slug__exact=slug, author__exact=request.user)
            if article.count() > 0:
                article = article[0]
            else:
                raise Article.DoesNotExist

            article.delete()
        except Article.DoesNotExist:
            raise NotFoundException("Article is not found.")
        return Response({"detail": "Article deleted."}, status=status.HTTP_204_NO_CONTENT)




