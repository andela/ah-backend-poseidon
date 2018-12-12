"""
Test articles app
"""
from django.urls import reverse
from rest_framework import status

from . import post_article, thread, comment

from authors.apps.tests.base import BaseTestCase


class TestComment(BaseTestCase):
    """
    test class to contain functions to handle test for the commenting on an article
    """

    def test_create_a_comment(self):
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        response = self.client.post(url, data=comment, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_single_comment(self):
        "This menthod tests getting a single comment"
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.get(
            f'/api/{slug}/comments/{comment_id}', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_reply_to_comment(self):
        """
            method to test for a reply to a comment

        """
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.post(
            f'/api/{slug}/comments/{comment_id}/thread',
            data=thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_reply_to_comment_with_no_body(self):
        """
            method to test for an empty reply.

        """
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.post(
            f'/api/{slug}/comments/{comment_id}/thread',
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_reply_to_comment(self):
        """
            testing for a single reply
            
        """
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.post(
            f'/api/{slug}/comments/{comment_id}/thread',
            data=thread,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(
            f'/api/{slug}/comments/{comment_id}/thread', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_a_comment_with_no_body(self):
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_comments(self):
        """
            test to get all comments
            
        """
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        response = self.client.get(url, data=comment, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    

    def test_delete_comment(self):
        """
            tests to delete a comment
        """
        self.user_access()
        self.posting_article(post_article)
        slug = self.slugger()
        url = f'/api/{slug}/comments/'
        res = self.client.post(url, data=comment, format="json")
        comment_id = res.data['id']
        response = self.client.delete(
            f'/api/{slug}/comments/{comment_id}', data=thread, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
