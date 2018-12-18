"""
Test comments app
"""
from django.urls import reverse
from rest_framework import status

from . import post_article, thread, comment

from authors.apps.tests.base import BaseTestCase


class TestCommentHistory(BaseTestCase):
    """
    This class tests the functions for editing
    comment and viewing history of edited comment
    """

    def test_get_all_comments(self):
        """
            test to get all edited comments

        """
        self.regiter_user_and_post_article()
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.get(
            f'/api/{slug}/comments/{comment_id}/history', data=comment, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_comment(self):
        """
            tests to updating a comment
        """
        self.regiter_user_and_post_article()
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.put(
            f'/api/{slug}/comments/{comment_id}', data=thread, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data['message'],
                      "This comment has been updated successfully")
