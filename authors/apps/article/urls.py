"""
Module defines urls used in article package
"""
from django.urls import path

from .views import ArticleAPIView, ArticleRetrieveAPIView, RatingsView

urlpatterns = [
    # article urls
    path("articles/", ArticleAPIView.as_view(), name="articles"),
    path("articles/<slug>/", ArticleRetrieveAPIView.as_view(), name="get_update_destroy_article"),
    # rating urls
    path("<slug>/rate/", RatingsView.as_view(), name="rating"),
]
