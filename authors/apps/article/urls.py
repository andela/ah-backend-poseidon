"""
Module defines urls used in article package
"""
from django.conf.urls import url
from django.urls import path

from .views import (ArticleAPIView, ArticleListView, ArticleRetrieveAPIView,
                    BookmarksAPIView, FavouritesAPIView, RatingsView,
                    ReportAPIViews, ReportArticleView, ReportList)

urlpatterns = [
    # article urls
    path("articles/", ArticleAPIView.as_view(), name="articles"),
    path(
        "articles/<slug>/",
        ArticleRetrieveAPIView.as_view(),
        name="get_update_destroy_article"),
    # rating urls
    path("<slug>/rate/", RatingsView.as_view(), name="rating"),
    path(
        "articles/<slug>",
        ArticleRetrieveAPIView.as_view(),
        name="get_update_destroy_article"),
    url(r'^articles?$', ArticleListView.as_view(), name="filter_articles"),
    # favouring article
    path('<slug>/favourite/', FavouritesAPIView.as_view(), name="favourite"),
    path(
        '<slug>/favourite/',
        FavouritesAPIView.as_view(),
        name="undo_favourite"),
    path(
        '<slug>/bookmark/',
        BookmarksAPIView.as_view(),
        name="bookmark_article"),
    path('bookmarks/', BookmarksAPIView.as_view(), name="bookmarked_articles"),
    path('report/<int:pk>/', ReportAPIViews.as_view(), name="single_report"),
    path('reports/', ReportList.as_view(), name="all_reports"),
    path(
        'articles/<int:pk>/report/',
        ReportArticleView.as_view(),
        name="report_article")
]
