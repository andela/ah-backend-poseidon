"""
Test articles app
"""
from django.urls import reverse

from authors.apps.tests.base import BaseTestCase

from . import (ARTICLE_URL, article_missing_data, post_article,
               update_article)


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
            reverse("articles"), data=article_missing_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())

    def test_no_articles(self):
        self.authorize_user()
        response = self.client.get(ARTICLE_URL, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('articles', response.json())
        self.assertIn(response.data['detail'],
                      'No articles found after search')

    def test_get_all_articles(self):
        self.authorize_user()
        count = 0
        while count < 3:
            self.posting_article(post_article)
            count += 1
        response = self.client.get(ARTICLE_URL, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_specific_article(self):
        slug = self.slugger2()
        response = self.client.get(
            reverse("get_update_destroy_article", kwargs=dict(slug=slug)),
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_get_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(ARTICLE_URL, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_update_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(ARTICLE_URL, format='json')
        data = response.json().get("articles")
        slug = data["results"][0]["slug"]
        response = self.client.put(
            reverse("get_update_destroy_article", kwargs=dict(slug=slug)),
            data=update_article,
            format='json')
        self.assertEqual(response.status_code, 202)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_delete_specific_article(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get(ARTICLE_URL, format='json')
        data = response.json().get("articles")
        slug = data["results"][0]["slug"]
        response = self.deleter(slug)
        self.assertEqual(response.status_code, 204)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)

    def test_delete_not_found_article(self):
        self.authorize_user()
        response = self.client.delete(
            reverse("get_update_destroy_article", kwargs=dict(slug="54")),
            format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)

    def test_search_by_author(self):
        """test filter by author name"""
        self.post_articles_for_search()
        response = self.client.get(ARTICLE_URL + '?author=Jac', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())

    def test_search_by_title(self):
        """test search by article title"""
        self.post_articles_for_search()
        response = self.client.get(
            ARTICLE_URL + '?title=Who is he', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_search_by_tags(self):
        """assert filter by tags"""
        self.post_articles_for_search()
        response = self.client.get(ARTICLE_URL + '?tags=python', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_search_by_keyword(self):
        """test search by keyword"""
        self.post_articles_for_search()
        response = self.client.get(
            ARTICLE_URL + '?keyword=Pythonis', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_search_multiple_params(self):
        """test search by multiple parameters"""
        self.post_articles_for_search()
        response = self.client.get(
            ARTICLE_URL + '?author=Jac&title=Pythonistas&tags=python',
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_search_by_non_existing_author(self):
        """check if username filtered against doesnot exist"""
        self.post_articles_for_search()
        response = self.client.get(ARTICLE_URL + '?author=Bill', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("articles", response.json())
        self.assertIn(response.data['detail'],
                      'No articles found after search')

    def test_search_by_non_existing_title(self):
        """check if article with title is not found"""
        self.post_articles_for_search()
        response = self.client.get(
            ARTICLE_URL + '?title=What about the world?', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("articles", response.json())
        self.assertIn(response.data['detail'],
                      'No articles found after search')
