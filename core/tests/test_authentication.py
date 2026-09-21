from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profile_app.tests.utils import create_user


class OptionalTokenAuthenticationTests(APITestCase):
    """A stale token counts as no token, a valid one still logs in."""

    def setUp(self):
        self.user = create_user('jane')
        self.profile_url = reverse('profile-detail', args=[self.user.id])

    def test_public_list_works_with_stale_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token deadbeef')
        response = self.client.get(reverse('offer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_endpoint_still_returns_401(self):
        for header in ['Token deadbeef', 'Token a b', 'Token']:
            self.client.credentials(HTTP_AUTHORIZATION=header)
            response = self.client.get(self.profile_url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED, header,
            )
            self.assertEqual(response['WWW-Authenticate'], 'Token')

    def test_valid_token_still_authenticates(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_of_inactive_user_counts_as_none(self):
        token = Token.objects.create(user=self.user)
        self.user.is_active = False
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(reverse('base-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
