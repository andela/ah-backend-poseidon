"""
Test on socialshare of application
"""
from django.urls import reverse
from rest_framework import status

from authors.apps.tests.base import BaseTestCase

from . import (ARTICLE_URL, article_missing_data, post_article,
               post_article_2, update_article)


class TestSocialShare(BaseTestCase):
    """
    test class to contain functions to handle test for article sharing on social media sites
    """

    def test_share_on_facebook(self):
        """
        test for successful share on facebook
        """
        self.user_access()
        slug = self.slugger()
        url = f'/api/{slug}/facebook'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_no_article_on_facebook(self):
        """
        this test checks for a failed share of a non existent article on facebook
        """
        self.user_access()
        url = f'/api/hhj/facebook'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_article_on_twitter(self):
        """
        check for a successful share on twitter
        """
        self.user_access()
        slug = self.slugger()
        url = f'/api/{slug}/twitter'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_no_article_on_twitter(self):
        """
        method to check a failed share on twitter
        """
        self.user_access()
        url = f'/api/hhj/twitter'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_share_article_via_email(self):
        """
        test to successfully share article via email
        """
        self.user_access()
        slug = self.slugger()
        url = f'/api/{slug}/email'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_article_via_wrong_email(self):
        """
        check for error when user tries to share an article that doesn't exist
        """
        self.user_access()
        url = f'/api/hhj/email'
        response = self.client.post(
            url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
