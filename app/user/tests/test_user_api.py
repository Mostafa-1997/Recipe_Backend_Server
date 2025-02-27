from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:login')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_username_exists_error(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': '1234',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user_using_email(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)

        login_details = {
            'login': 'testuser',
            'password': 'testpass',
        }

        res = self.client.post(TOKEN_URL, login_details)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_user_using_username(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }
        create_user(**payload)

        login_details = {
            'login': 'test@test.com',
            'password': 'testpass',
        }

        res = self.client.post(TOKEN_URL, login_details)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def token_create_token_bad_credentials(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }

        create_user(**payload)

        invalid_payload = {
            'login': 'test@test.com',
            'password': '123',
        }

        res = self.client.post(TOKEN_URL, invalid_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_payload = {
            'login': 'testuser',
            'password': '123',
        }

        res = self.client.post(TOKEN_URL, invalid_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):

        payload = {
            'login': 'test@test.com',
            'password': '',
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):

        payload = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'testpass',
            'name': 'Test Name'
        }

        create_user(**payload)

        invalid_payload = {
            'login': 'example@test.com',
            'password': 'testpass',
        }

        res = self.client.post(TOKEN_URL, invalid_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        invalid_payload = {
            'login': 'test',
            'password': 'testpass',
        }

        res = self.client.post(TOKEN_URL, invalid_payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            username='testuser',
            password='testpass',
            name='Test Name',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'username': self.user.username,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):

        payload = {
            'name': 'New Name',
            'password': 'newpassword'
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
