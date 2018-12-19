from django.urls import path
from .views import (CommentCreateListView, CommentsListThreadsCreateView,
                    CommentsAPIView, CommentHistoryListView)
from authors.apps.article.models import LikeDislike, LikeDislikeManager, Article
from authors.apps.article.views import ChoicesView
from .serializers import CommentSerializer, Comment

app_name = 'comments'
urlpatterns = [
    path(
        '<slug>/comments/',
        CommentCreateListView.as_view(),
        name='post_comment'),
    path(
        '<slug>/comments/<int:id>',
        CommentsAPIView.as_view(),
        name='single_comment'),
    path(
        '<slug>/comments/<int:id>/thread',
        CommentsListThreadsCreateView.as_view(),
        name='thread_comment'),
    path(
        '<slug>/comments/<int:id>/history',
        CommentHistoryListView.as_view(),
        name='comment_history'),
    path(
        'comments/<pk>/like/',
        ChoicesView.as_view(
            model=Comment,
            vote_type=LikeDislike.LIKE,
            manager=LikeDislikeManager,
            serializer=CommentSerializer),
        name='comment_like'),
    path(
        'comments/<pk>/dislike/',
        ChoicesView.as_view(
            model=Comment,
            vote_type=LikeDislike.DISLIKE,
            manager=LikeDislikeManager,
            serializer=CommentSerializer),
        name='comment_dislike'),
]
