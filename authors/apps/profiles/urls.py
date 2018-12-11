from django.urls import path
from .views import ProfileRetrieveAPIView, FollowAuthorAPIView

urlpatterns = [
    path(
        'profiles/<username>',
        ProfileRetrieveAPIView.as_view(),
        name="get_profile"),
    path(
        'profiles/<username>/follow',
        FollowAuthorAPIView.as_view(),
        name="user_follow"),
]
