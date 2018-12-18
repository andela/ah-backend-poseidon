from django.shortcuts import get_object_or_404, render
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from authors.apps.article.models import Article

from .models import Comment
from .renderer import (CommentJSONRenderer, CommentThreadJSONRenderer)
from .serializers import (CommentSerializer, CommentChildSerializer,
                          CommentHistorySerializer)
from .utils import HighlightedSection


class CommentCreateListView(generics.ListCreateAPIView):
    """

    create comments and retrieve comments 

    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )
    queryset = Comment.objects.all().filter(parent__isnull=True)
    lookup_field = 'slug'
    highlighted_section = HighlightedSection()

    def post(self, request, *args, **kwargs):
        """
        This method posts a comment to article
        """
        comment, slug = self.highlighted_section.get_selected_text(
            request, self.kwargs['slug'])
        serializer = self.serializer_class(data=comment, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(commented_by=self.request.user, slug=slug)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        article_slug = self.kwargs['slug']
        slug = get_object_or_404(Article, slug=article_slug)
        comment = self.queryset.filter(slug=article_slug)
        serializer = self.serializer_class(comment, many=True)
        return Response(serializer.data)


class CommentsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )
    lookup_fields = 'id', 'slug'
    queryset = Comment.objects.all().filter(parent__isnull=True)

    def destroy(self, request, *args, **kwargs):
        article_slug = self.kwargs['slug']
        slug = get_object_or_404(Article, slug=article_slug)
        instance = self.get_object()
        self.check_user(instance, request)
        self.perform_destroy(instance)
        return Response({
            "message": "This comment has been deleted successfully"
        },
            status=status.HTTP_200_OK)

    def check_user(self, instance, request):
        if instance.commented_by != request.user:
            raise PermissionDenied

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)

    def update(self, request, *args, **kwargs):
        """
        This function updates a given comment
        for an article with given id and slag
        """
        comment = request.data.get("comment", {})
        article_slug = self.kwargs['slug']
        slug = get_object_or_404(Article, slug=article_slug)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=comment, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        smg = "This comment has been updated successfully"
        return Response({
            "message": smg
        }, status=status.HTTP_200_OK)


class CommentsListThreadsCreateView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CommentChildSerializer
    renderer_classes = (CommentThreadJSONRenderer, )
    lookup_fields = 'id', 'slug'
    queryset = Comment.objects.all().filter(parent__isnull=False)

    def post(self, request, *args, **kwargs):
        article_slug = self.kwargs['slug']
        slug = get_object_or_404(Article, slug=article_slug)
        thread = request.data.get('comment', {})
        thread['parent'] = self.kwargs['id']
        serializer = self.serializer_class(data=thread, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(commented_by=self.request.user, slug=slug)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        article_slug = self.kwargs['slug']
        slug = get_object_or_404(Article, slug=article_slug)
        comment = self.queryset.filter(
            slug=article_slug, parent=self.kwargs['id'])
        serializer = self.serializer_class(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentHistoryListView(generics.ListCreateAPIView):
    """
    Retrieve comments history with
    comment id
    """
    serializer_class = CommentHistorySerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)

    def get(self, request, *args, **kwargs):
        id = self.kwargs['id']
        comment = Comment.history.filter(id=id)
        serializer = self.serializer_class(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
