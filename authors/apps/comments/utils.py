from django.shortcuts import get_object_or_404
from rest_framework.serializers import ValidationError
from authors.apps.article.models import Article


class HighlightedSection():
    """
    This class has a method that highlights a text from an article's body
    """
    def get_selected_text(self, request, slug):
        """
        This method stores the higlighted text and appends it to a comment
        """
        article_slug = get_object_or_404(Article, slug=slug)
        comment = request.data.get('comment', {})
        if 'start_index_position' and 'end_index_position' in comment:
            try:
                selection = self.select_index(
                    int(comment.get('start_index_position', 0)),
                    int(comment.get('end_index_position', 0)))
            except ValueError:
                raise ValidationError({
                    "message":
                    "Please use integer values to select a start position and end position"
                })
            selected_text = str(article_slug.body[selection[0]:selection[1]])
            comment['selected_text'] = selected_text
        return comment, article_slug

    def select_index(self, start_position, end_position):
        """
        method picks the selected index values, stores them in a variable
        """
        index_values = [start_position, end_position]
        if start_position > end_position:
            index_values = [end_position, start_position]
        return index_values
