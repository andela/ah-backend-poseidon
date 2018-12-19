import os
from django.http import Http404
from django.core.mail import send_mail
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import Http404, get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly, IsAdminUser)
from rest_framework.response import Response

from authors.apps.article.exceptions import (NotFoundException)
from authors.apps.article.models import Article, Report
from authors.apps.article.renderer import ArticleJSONRenderer
from authors.apps.article.serializers import (
    ArticleSerializer, PaginatedDataSerializer, RatingSerializer,
    ReportSerializer)
from .utils import invalid_string, check_if_report_exists
from .filters import ArticleFilter
from .utils import bookmark_validator
from django.contrib.contenttypes.models import ContentType
from .models import LikeDislike


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
        article.update({"author": request.user.pk})
        serializer = self.serializer_class(data=article, )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        """
        returns a specific article based on the slug
        """
        queryset = Article.objects.all()
        article = get_object_or_404(queryset, slug=slug)
        author = True

        # check if the user who is viewing the article is the not the author
        # if he is not the author we increase on the number
        # of views the article has been
        # read whenever a get request is run.
        if article.author.username != request.user.username:
            article.view_counts += 1
            article.save()
            author = False
        serializer = self.serializer_class(
            article, context={'request': request})

        if not author:
            serializer.fields.pop('view_counts', None)
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
        if not serializer.data:
            return Response({
                "detail": "No articles found after search"
            },
                            status=status.HTTP_404_NOT_FOUND)

        page_class = PaginatedDataSerializer()
        page_class.page_size = 3

        return Response(
            page_class.get_paginated_response(
                page_class.paginate_queryset(serializer.data, request)))


class FavouritesAPIView(generics.GenericAPIView):
    """
    Handles methods involved with selecting an article as a favourite
    """
    permission_classes = (IsAuthenticated, )

    def put(self, request, slug=None):
        profile = self.request.user.profile
        serializer_context = {"request": request}
        try:
            article = Article.objects.get(slug=slug)
            if article.author == request.user:
                return Response(
                    {
                        "message": "Please favourite another author's article",
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            raise NotFound("Article not found")
        if profile.is_favourite(article):
            return Response({
                "message": "Article is already your favourite"
            },
                            status=status.HTTP_400_BAD_REQUEST)

        # add the article to the user profile as favourite
        profile.favourite(article)
        # to increment the favourites count field in articles
        article.favourites_count += 1
        article.save()
        serializer = ArticleSerializer(
            article, context=serializer_context, partial=True)
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
            },
                            status=status.HTTP_404_NOT_FOUND)

        profile.not_favourite(article=article)
        article.favourites_count = article.favourites_count-1 \
            if article.favourites_count > 0 else 0
        article.save()

        serializer = ArticleSerializer(article, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BookmarksAPIView(generics.GenericAPIView):
    """
    Views for bookmark requests
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, slug=None):
        try:
            article = Article.objects.get(slug=slug)
            rv = bookmark_validator(article, request)
            if rv is None:
                article.bookmark(request.user)
                return Response({
                    "message": "Article bookmarked"
                },
                                status=status.HTTP_201_CREATED)
            return rv
        except Article.DoesNotExist:
            raise NotFound("Article not found")

    def get(self, request):
        user = request.user
        queryset = Article.objects.filter(bookmarks__id=user.pk)
        serializer = ArticleSerializer(queryset, many=True)
        if not serializer.data:
            return Response({
                "message": "No articles bookmarked yet"
            },
                            status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request, slug=None):
        try:
            article = Article.objects.get(slug=slug)
            user = request.user
            article.unbookmark(user)
            return Response({
                "message": "Article unbookmarked"
            },
                            status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            raise NotFound("Article not in bookmark list")


class ReportList(generics.ListCreateAPIView):
    """
    Return all reports for admin.
    """
    permission_classes = (IsAdminUser, )
    serializer_class = ReportSerializer

    def list(self, request):
        query = Report.objects.all()
        serializer = ReportSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportAPIViews(generics.GenericAPIView):
    """
    Functions used by admin to handle reports
    """
    permission_classes = (IsAdminUser, )
    serializer_class = ReportSerializer

    def get(self, request, pk):
        query = check_if_report_exists(Report, pk)
        serializer = ReportSerializer(query)
        query.viewed = True
        query.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = check_if_report_exists(Report, pk)
        serializer = ReportSerializer(query)
        query.violation = True
        query.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        query = check_if_report_exists(Report, pk)
        query.delete()
        return Response({
            "details": "Report has been deleted"
        },
                        status=status.HTTP_200_OK)


class ReportArticleView(generics.GenericAPIView):
    """
    View for user to report article
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = ReportSerializer

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise NotFoundException
        mes = request.data.get('report', {})
        new_text = str(mes['message']).strip()
        if not new_text:
            return Response({
                "details": invalid_string
            },
                            status=status.HTTP_400_BAD_REQUEST)
        report = Report(
            article=article, reported_by=request.user, message=new_text)
        report.save()
        serializer = ReportSerializer(report)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChoicesView(generics.GenericAPIView):
    "Implements the like and dislike endpoints."
    model = None
    vote_type = None
    manager = None

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        try:
            likedislike = LikeDislike.objects.get(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])

            else:
                likedislike.delete()

        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
        serializer = ArticleSerializer(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
class ShareArticleViaFacebookAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]

        try:
            Article.objects.get(slug=slug)
            base_url = "https://www.facebook.com/sharer/sharer.php?u="
            url_param = os.environ.get(
                'BASE_URL', 'http://127.0.0.1:8000/api/articles/{}'.format(slug))
            url_link = base_url + url_param
            return Response(
                {
                    "message": "Article successfully shared on facebook",
                    "link": url_link
                },
                status=status.HTTP_200_OK
            )
        except:
            return Response({
                "message": "Article not found. Please try again"
            }, status=status.HTTP_404_NOT_FOUND)


class ShareArticleViaTwitterAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]
        try:
            Article.objects.get(slug=slug)
            base_url = "https://twitter.com/home?status=Authors%20Heaven%20has%20shared%20an%20article%20"
            url_param = os.environ.get(
                'BASE_URL', 'http://127.0.0.1:8000/api/articles/{}'.format(slug))
            url_link = base_url + url_param
            return Response(
                {
                    "message": "Twitter link",
                    "link": url_link
                },
                status=status.HTTP_200_OK
            )
        except:
            return Response({
                "message": "Article not found. Please try again"
            }, status=status.HTTP_404_NOT_FOUND)


class ShareArticleViaEmailView(generics.CreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = "slug"

    def post(self, request, *args, **kwargs):

        slug = self.kwargs["slug"]
        try:
            Article.objects.get(slug=slug)
            url_param = os.environ.get(
                'BASE_URL', 'http://127.0.0.1:8000/api/articles/{}'.format(slug))

            sending_email = os.getenv(
                "EMAIL_HOST_USER", "teamposeidon12@gmail.com")
            recipient_email = request.user.email
            subject = "Authors Haven article link"
            body = " Click here to view the shared article {}/".format(
                url_param)
            send_mail(subject, body, sending_email, [
                      recipient_email], fail_silently=False)

            return Response(
                {
                    "message": "Article successfully shared. Please check your email to view the article"
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response({
                "message": "Article not found. Please try again"
            }, status=status.HTTP_404_NOT_FOUND)
