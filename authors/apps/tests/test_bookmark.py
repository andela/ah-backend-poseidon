from django.urls import reverse
from authors.apps.tests.base import BaseTestCase
from . import ARTICLE_URL


class BookmarksTestCase(BaseTestCase):
    """tests for bookmarks"""

    def test_bookmark_article(self):
        """test if article is bookmarked"""
        url = self.url_for_bookmarks()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertIn(response.data['message'], 'Article bookmarked')

    def test_get_bookmarked_articles(self):
        """fetch bookmarked articles test"""
        url = self.url_for_bookmarks()
        self.client.post(url)
        url2 = reverse('bookmarked_articles')
        response = self.client.get(url2)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_unbookmark_article(self):
        """assert article unbookmarked"""
        url = self.url_for_bookmarks()
        self.client.post(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.data['message'], 'Article unbookmarked')

    def test_already_bookmarked(self):
        """assert article already bookmarked"""
        url = self.url_for_bookmarks()
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.data['message'],
                      'Article already bookmarked by you')

    def test_no_articles_bookmarked(self):
        """test no articles bookmarked"""
        self.post_articles_for_search()
        self.authorize_user2()
        url = reverse('bookmarked_articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.data['message'], 'No articles bookmarked yet')

    def test_article_not_found(self):
        """check specific article not found for bookmarking"""
        url = self.url_for_invalid_slug()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.data['detail'], 'Article not found')

    def test_unbookmark_article_not_bookmarked(self):
        """assert article not bookmarked can't be unbookmarked"""
        url = self.url_for_invalid_slug()
        self.client.post(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.data['detail'], 'Article not in bookmark list')

    def test_bookmark_own_article(self):
        """check if author can't bookmark their article"""
        self.post_articles_for_search()
        article_data = self.client.get(ARTICLE_URL, format='json')
        data = article_data.json().get("articles")
        slug = data["results"][0]["slug"]
        url = reverse('bookmark_article', kwargs={'slug': slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.data['message'],
                      "You can't bookmark your own article")
