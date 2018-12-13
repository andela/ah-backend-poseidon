from django.urls import path
from .views import (CommentCreateListView, CommentsListThreadsCreateView,
                    CommentsAPIView, CommentHistoryListView)

app_name = 'comments'
urlpatterns = [
    path('<slug>/comments/', CommentCreateListView.as_view(), name='comments'),
    path(
        '<slug>/comments/<int:id>',
        CommentsAPIView.as_view(),
        name='single_comment'),
    path(
        '<slug>/comments/<int:id>/thread',
        CommentsListThreadsCreateView.as_view(),
        name='thread_comment'),
    path('<slug>/comments/<int:id>/history',
         CommentHistoryListView.as_view(),
         name='comment_history'),
]
