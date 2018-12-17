"""
module to test favourites feature
"""
from django.urls import reverse

from authors.apps.tests import post_article, ARTICLE_URL
from authors.apps.tests.base import BaseTestCase


class TestFavouriteArticle(BaseTestCase):
    """
    test class to contain functions to test favouring an article
    """

    def setUp(self):
        self.authorize_user()
        self.posting_article(post_article)
        self.article_data = self.client.get(ARTICLE_URL, format='json')
        data = self.article_data.json().get("articles")
        self.slug = data["results"][0]["slug"]

    def test_favourite_your_article(self):
        """
        method to test favouring your own article
        """
        response = self.favouring(slug=self.slug)
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)

    def test_favourite_someones_article(self):
        """
        method to test favouring someone's article
        """
        self.authorize_user2()
        response = self.favouring(slug=self.slug)
        self.assertEqual(response.status_code, 201)

    def test_favouring_article_not_found(self):
        """
        method to test favouring an article that does not exist
        """
        self.authorize_user2()
        response = self.client.put(
            reverse("favourite", kwargs=dict(slug=self.slug+"-wqerwr")),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_undo_favouring_article_not_found(self):
        """
        method to test undoing favourite to an article that does not exist
        """
        self.authorize_user2()
        response = self.client.delete(
            reverse("favourite", kwargs=dict(slug=self.slug+"-wqerwr")),
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_already_favourite(self):
        """
        method to test for favouring an article that is already a favourite
        """
        self.authorize_user2()
        self.favouring(slug=self.slug)
        response = self.favouring(slug=self.slug)
        self.assertEqual(response.status_code, 400)

    def test_undo_favourite_article(self):
        """
        method to test changing an article from favourite to not favourite
        """
        self.authorize_user2()
        self.favouring(slug=self.slug)
        response = self.undo_favouring(slug=self.slug)
        self.assertEqual(response.status_code, 200)

    def test_article_not_in_favourites(self):
        """
        method to test an not favouring an article absent in your favourites list
        """
        self.authorize_user2()
        response = self.undo_favouring(slug=self.slug)
        self.assertEqual(response.status_code, 404)
