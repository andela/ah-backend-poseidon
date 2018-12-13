"""
test module for rating an article
"""
from django.urls import reverse

from authors.apps.tests import post_article
from authors.apps.tests.base import BaseTestCase
from . import ARTICLE_URL


class TestRatingArticle(BaseTestCase):
    """
    test class to contain functions to test rating an article
    """

    def setUp(self):
        self.authorize_user()
        self.posting_article(post_article)
        self.article_data = self.client.get(ARTICLE_URL, format='json')
        data = self.article_data.json().get("articles")[0]
        self.slug = data["slug"]

    def test_rate_your_article(self):
        """
        method to test rating your own article
        """
        response = self.client.post(
            reverse("rating", kwargs=dict(slug=self.slug)),
            data={"article": {"score": 3}},
            format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_rate_someones_article(self):
        """
        method to test rating someone's article
        """
        self.authorize_user2()
        response = self.client.post(
            reverse("rating", kwargs=dict(slug=self.slug)),
            data={"article": {"score": 3}},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())

    def test_rate_out_of_range(self):
        """
        method to test rating an article using out of range values
        """
        response = self.rate_article(rating=6)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_rate_article_not_found(self):
        """
        method to test rating an article that does not exist
        """
        self.authorize_user2()
        response = self.client.post(
            reverse("rating", kwargs=dict(slug=self.slug+"-wqerwr")),
            data={"article": {"score": 3}},
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("articles", response.json())

    def test_rate_article_already_rated(self):
        """
        method to test rating an article already rated
        """
        self.authorize_user2()
        # rate article the first time
        self.client.post(
            reverse("rating", kwargs=dict(slug=self.slug)),
            data={"article": {"score": 3}},
            format="json"
        )
        # rate article the second time
        response = self.client.post(
            reverse("rating", kwargs=dict(slug=self.slug)),
            data={"article": {"score": 4}},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
