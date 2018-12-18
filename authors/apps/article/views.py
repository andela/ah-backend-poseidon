from django.http import Http404
from rest_framework import status, generics

# Create your views here.
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.generics import Http404, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authors.apps.article.exceptions import NotFoundException
from authors.apps.article.models import Article
from authors.apps.article.renderer import ArticleJSONRenderer
from authors.apps.article.serializers import (ArticleSerializer,
                                              RatingSerializer)

from .filters import ArticleFilter


class ArticleAPIView(generics.CreateAPIView):
    """
    Article ViewSet
    Handles all CRUD operations
    """
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def post(self, request):
        """
        creates an article
        """
        article = request.data.get("article", {})
        article.update({"author": request.user.pk})  # request.user.pk
        serializer = self.serializer_class(data=article, )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        """
        returns a specific article based on the slug
        """
        queryset = Article.objects.all()
        article = get_object_or_404(queryset, slug=slug)

        serializer = self.serializer_class(
            article, context={'request': request})
        return Response(serializer.data)

    def update(self, request, slug=None):
        """
        update a specific article
        """
        article_update = request.data.get("article", {})

        article, article_update = \
            self.serializer_class.validate_for_update(
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
        return Response({
            "detail": "Article deleted."
        },
            status=status.HTTP_204_NO_CONTENT)


class RatingsView(generics.GenericAPIView):
    """
    implements methods to handle rating articles
    """
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )

    def post(self, request, slug=None):
        """
        method to post a rating for an article
        """
        data = self.serializer_class.update_data(
            request.data.get("article", {}), slug, request.user)

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleListView(generics.ListAPIView):
    """
    Filter articles
    """
    permission_classes = (AllowAny, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = ArticleFilter

    def list(self, request):
        """
        returns a list of all articles, allows filtering and custom searching
        """
        queryset = Article.objects.all()
        queryset = self.filter_queryset(queryset)
        serializer = ArticleSerializer(queryset, many=True)
        if serializer.data == []:
            return Response({
                "detail": "No articles found after search"
            },
                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavouritesAPIView(generics.GenericAPIView):
    """
    Handles methods involved with selecting aan article as a favourite
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = ArticleSerializer

    def post(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {"request": request}
        try:
            article = Article.objects.get(slug=slug)
            if article.author == request.user:
                return Response({
                    "message": "Please favourite another author's article",
                }, status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            raise NotFound("Article not found")
        if profile.is_favourite(article):
            return Response({
                "message": "Article is already your favourite"
            }, status=status.HTTP_400_BAD_REQUEST)

        # add the article to the user profile as favourite
        profile.favourite(article)
        # to increment the favourites count field in articles
        article.favourites_count += 1
        article.save()
        serializer = self.serializer_class(article, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {"request": request}

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("Article not found")

        if not profile.is_favourite(article=article):
            return Response({
                "message": "Article is not your favourites list"
            }, status=status.HTTP_404_NOT_FOUND)

        profile.not_favourite(article=article)
        article.favourites_count = article.favourites_count-1 \
            if article.favourites_count > 0 else 0
        article.save()

        serializer = self.serializer_class(article, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)
