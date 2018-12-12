"""
Module defines urls used in article package
"""
from django.conf.urls import url
from django.urls import path

from .views import (ArticleAPIView, ArticleListView, ArticleRetrieveAPIView,
                    RatingsView, FavouritesAPIView)

urlpatterns = [
    # article urls
    path("articles/", ArticleAPIView.as_view(), name="articles"),
    path("articles/<slug>/", ArticleRetrieveAPIView.as_view(),
         name="get_update_destroy_article"),
    # rating urls
    path("<slug>/rate/", RatingsView.as_view(), name="rating"),
    path(
        "articles/<slug>",
        ArticleRetrieveAPIView.as_view(),
        name="get_update_destroy_article"),
    url(r'^articles?$', ArticleListView.as_view(), name="filter_articles"),
    # favouring article
    path('<slug>/favourite/',
         FavouritesAPIView.as_view(), name="favourite"),
    path('<slug>/favourite/',
         FavouritesAPIView.as_view(), name="undo_favourite"),
]
