from django.urls import path
from .views import (ProfileRetrieveAPIView, FollowAuthorAPIView,
                    NotificationRetrieveAPIView, UserNotificationsView,
                    ListAuthorsAPIView, FollowersAPIView, FollowsAPIView)

urlpatterns = [
    path(
        'profiles/<username>',
        ProfileRetrieveAPIView.as_view(),
        name="get_profile"),
    path(
        'profiles/<username>/follow',
        FollowAuthorAPIView.as_view(),
        name="user_follow"),
    path('profiles/', ListAuthorsAPIView.as_view(), name="users_profiles"),
    path(
        'user/notifications/', UserNotificationsView.as_view(), name='notify'),
    path(
        'notifications/<int:pk>/',
        NotificationRetrieveAPIView.as_view(),
        name='single_notify'),
    path('user/followers', FollowersAPIView.as_view(), name="user_followers"),
    path('user/following', FollowsAPIView.as_view(), name="user_following"),
]
