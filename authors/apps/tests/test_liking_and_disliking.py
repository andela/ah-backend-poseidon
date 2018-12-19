from django.urls import reverse
from rest_framework import status
from .base import BaseTestCase
from . import post_article


class ArticleLikeDislikeTestCase(BaseTestCase):

    def setUp(self):
        pk_slug = self.create_article_for_liking()
        self.pk = pk_slug[0]

    # Tests liking an article
    def test_liking_an_article(self):
        response = self.client.post(
            reverse('article_like', kwargs={'pk': self.pk}))
        self.assertEqual(response.data['likes'], 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Tests liking an article that a user already liked
    def test_user_already_liked_an_article(self):
        self.client.post(reverse('article_like', kwargs={'pk': self.pk}))
        response = self.client.post(
            reverse('article_like', kwargs={'pk': self.pk}))
        self.assertEqual(response.data['likes'], 0)

    # # Tests disliking an article that a user already disliked
    def test_user_already_disliked_an_article(self):
        self.client.post(reverse('article_dislike', kwargs={'pk': self.pk}))
        response = self.client.post(
            reverse('article_dislike', kwargs={'pk': self.pk}))
        self.assertEqual(response.data['dislikes'], 0)

    # # Tests disliking an article
    def test_disliking_an_article(self):
        response = self.client.post(
            reverse('article_dislike', kwargs={'pk': self.pk}))
        self.assertEqual(response.data['dislikes'], 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # # Tests a user liking an article that they first disliked
    def test_liking_when_already_disliked_an_artcle(self):
        self.client.post(reverse('article_dislike', kwargs={'pk': self.pk}))
        res = self.client.post(
            reverse('article_like', kwargs={'pk': self.pk}))
        self.assertEqual(res.data['dislikes'], 0)
        self.assertEqual(res.data['likes'], 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # Tests a user disliking an article that they first liked
    def test_disliking_when_already_liked_an_artcle(self):
        self.client.post(reverse('article_like', kwargs={'pk': self.pk}))
        res = self.client.post(
            reverse('article_dislike', kwargs={'pk': self.pk}))
        self.assertEqual(res.data['likes'], 0)
        self.assertEqual(res.data['dislikes'], 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class CommentLikeDislikeTestCase(BaseTestCase):

    def setUp(self):
        pk = self.post_comment()
        self.like_url = '/api/comments/{}/like/'.format(pk)
        self.dislike_url = '/api/comments/{}/dislike/'.format(pk)

    # Tests liking a comment
    def test_liking_a_comment(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.data['likes'], 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Tests liking a comment that a user already liked
    def test_user_already_liked_a_comment(self):
        self.client.post(self.like_url)
        response = self.client.post(self.like_url)
        self.assertEqual(response.data['likes'], 0)

    # Tests disliking a comment that a user already disliked
    def test_user_already_disliked_a_comment(self):
        self.client.post(self.dislike_url)
        response = self.client.post(self.dislike_url)
        self.assertEqual(response.data['dislikes'], 0)

    # Tests disliking a comment
    def test_disliking_an_article(self):
        response = self.client.post(self.dislike_url)
        self.assertEqual(response.data['dislikes'], 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Tests a user liking a comment that they first disliked
    def test_liking_when_already_disliked_an_artcle(self):
        self.client.post(self.dislike_url)
        res = self.client.post(self.like_url)
        self.assertEqual(res.data['dislikes'], 0)
        self.assertEqual(res.data['likes'], 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # # Tests a user disliking a comment that they first liked
    def test_disliking_when_already_liked_an_artcle(self):
        self.client.post(self.like_url)
        res = self.client.post(self.dislike_url)
        self.assertEqual(res.data['likes'], 0)
        self.assertEqual(res.data['dislikes'], 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
