# Create your models here.
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from authors.apps.article.models import Article
from authors.apps.authentication.models import User
from simple_history.models import HistoricalRecords
from authors.apps.article.models import LikeDislike


class Comment(models.Model):
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.ForeignKey(
        Article, on_delete=models.CASCADE, to_field='slug')
    body = models.TextField()
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    selected_text = models.TextField(blank=True, null=True)
    start_index_position = models.IntegerField(blank=True, null=True)
    end_index_position = models.IntegerField(blank=True, null=True)
    history = HistoricalRecords()
    votes = GenericRelation(LikeDislike, related_query_name='comments')

    def __str__(self):
        return str(self.commented_by.username)

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not True:
            return False
        return True
