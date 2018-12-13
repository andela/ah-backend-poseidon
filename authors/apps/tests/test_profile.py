from django.urls import reverse
from rest_framework import status
from .test_validation import BaseTestCase
from . import new_user, new_user_2


class ProfileTestCase(BaseTestCase):
    "Handles users' profiles tests."

    def test_get_user_profile(self):
        "Tests getting of a user profile."

        self.register_user(new_user)
        url = reverse('get_profile', kwargs={'username': 'Jac'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_list_all_users_profiles(self):
        "Tests listing all profiles."

        self.authorize_user()
        url = reverse('users_profiles')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_who_does_not_exist(self):
        "Tests getting profile of a user who is not registered."

        response = self.client.get(
            reverse('get_profile', kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_profile(self):
        "Tests updating of a user profile."

        url = reverse('retrieve_user')
        self.authorize_user()

        response = self.client.put(
            url,
            data={
                "user": {
                    "username": "jackson",
                    "email": "jack@dev.com",
                    "bio": "coder"
                }
            },
            format='json')
        self.assertEqual(response.data['bio'], 'coder')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserFollowingTestCase(BaseTestCase):
    def test_follow_user(self):
        "Tests if users a can follow each other."

        self.register_user(new_user_2)
        self.authorize_user()

        response = self.client.post(
            reverse('user_follow', kwargs={'username': 'John'}))
        self.assertTrue(response.data['following'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_a_user_following_themselves(self):
        "Tests if a user can follow themselves."

        self.authorize_user()

        response = self.client.post(
            reverse('user_follow', kwargs={'username': 'Jac'}))
        self.assertIn('You can not follow yourself.',
                      response.data['errors']['detail'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user(self):
        "Tests unfollowing of users."

        self.register_user(new_user_2)
        self.authorize_user()
        self.client.post(reverse('user_follow', kwargs={'username': 'John'}))

        response = self.client.delete(
            reverse('user_follow', kwargs={'username': 'John'}))
        self.assertFalse(response.data['following'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow_or_unfollow_user_who_does_not_exist(self):
        "Tests following of a user who does not exist."

        self.authorize_user()

        response = self.client.post(
            reverse('user_follow', kwargs={'username': 'Joan'}))
        self.assertIn(
            'Profile does not exist. Check provided username.',
            response.data['errors']['detail'])

        response = self.client.delete(
            reverse('user_follow', kwargs={'username': 'Joan'}))
        self.assertIn(
            'Profile does not exist. Check provided username.',
            response.data['errors']['detail'])

    def test_getting_user_followers(self):
        res = self.followers_and_following()
        self.add_credentials(res.data['token'])
        response = self.client.get(reverse('user_followers'))
        self.assertIn('followers', response.data)

    def test_getting_users_a_user_is_following_when_empty(self):
        res = self.followers_and_following()
        self.add_credentials(res.data['token'])
        response = self.client.get(reverse('user_following'))
        self.assertIn('Currently you have no follows.',
                      response.data['following'])

    def test_getting_users_a_user_is_following_when_not_empty(self):
        self.followers_and_following()
        response = self.client.get(reverse('user_following'))
        self.assertIn('following', response.data)
        