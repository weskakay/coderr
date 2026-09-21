from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profile_app.tests.utils import create_user


class LoginTests(APITestCase):
    """Covers POST /api/login/."""

    def setUp(self):
        self.url = reverse('login')
        self.user = create_user('jane')

    def test_login_returns_200_with_token(self):
        payload = {'username': 'jane', 'password': 'pw12345!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'token': Token.objects.get(user=self.user).key,
            'username': 'jane',
            'email': 'jane@example.com',
            'user_id': self.user.id,
        })

    def test_login_reuses_existing_token(self):
        token = Token.objects.create(user=self.user)
        payload = {'username': 'jane', 'password': 'pw12345!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.data['token'], token.key)

    def test_wrong_password_returns_400(self):
        payload = {'username': 'jane', 'password': 'wrong'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_unknown_username_returns_400(self):
        payload = {'username': 'nobody', 'password': 'pw12345!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_is_not_accepted_as_username(self):
        payload = {'username': 'jane@example.com', 'password': 'pw12345!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stale_token_header_does_not_block_login(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token deadbeef')
        payload = {'username': 'jane', 'password': 'pw12345!'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_fields_return_400(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('password', response.data)
