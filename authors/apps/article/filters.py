from django_filters import FilterSet
from django_filters import rest_framework as filters

from .models import Article


class ArticleFilter(FilterSet):
    """custom filter class for Articles"""
    title = filters.CharFilter('title')
    keyword = filters.CharFilter('title', 'icontains')
    author = filters.CharFilter('author__username')
    tags = filters.CharFilter('tags', method='tags_filter')

    class Meta:
        model = Article
        fields = ['title', 'author', 'keyword', 'tags']

    def tags_filter(self, queryset, name, value):
        return queryset.filter(tags__name__icontains=value)
