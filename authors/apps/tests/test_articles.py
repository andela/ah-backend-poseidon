"""
Test articles app
"""
from django.urls import reverse

from . import update_article, article_missing_data, post_article, new_user, user_login

from authors.apps.tests.base import BaseTestCase


class TestArticle(BaseTestCase):
    """
    test class to contain functions to handle test for the article
    """
    def test_post_new_article(self):
        self.authorize_user()
        response = self.posting_article(post_article)
        self.assertEqual(201, response.status_code)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_post_article_with_missing_data(self):
        self.authorize_user()
        response = self.client.post(
            reverse("articles"),
            data=article_missing_data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())

    def test_no_articles(self):
        self.authorize_user()
        response = self.client.get(reverse("articles"), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), list)

    def test_get_all_articles(self):
        self.authorize_user()
        count = 0
        while count < 3:
            self.posting_article(post_article)
            count += 1
        response = self.client.get(reverse("articles"), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("articles")), 3)

    def test_get_specific_article(self):
        slug = self.slugger()
        response = self.client.get(
            reverse("get_update_destroy_article", kwargs=dict(slug=slug)),
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_get_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(reverse("articles"), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), list)

    def test_update_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(reverse("articles"), format='json')
        data = response.json().get("articles")[0]
        slug = data["slug"]
        response = self.client.put(reverse(
            "get_update_destroy_article",
            kwargs=dict(slug=slug)),
            data=update_article,
            format='json'
        )
        self.assertEqual(response.status_code, 202)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_delete_specific_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(reverse("articles"), format='json')
        data = response.json().get("articles")[0]
        slug = data["slug"]
        response = self.deleter(slug)
        self.assertEqual(response.status_code, 204)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)

    def test_delete_not_found_article(self):
        self.authorize_user()
        response = self.client.delete(reverse(
            "get_update_destroy_article",
            kwargs=dict(slug="54")),
            format='json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)
