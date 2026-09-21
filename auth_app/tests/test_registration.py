from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profile_app.models import Profile


class RegistrationTests(APITestCase):
    """Covers POST /api/registration/."""

    def setUp(self):
        self.url = reverse('registration')
        self.payload = {
            'username': 'jane',
            'email': 'jane@example.com',
            'password': 'asdasd',
            'repeated_password': 'asdasd',
            'type': 'customer',
        }

    def test_registration_returns_201_with_token(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='jane')
        self.assertEqual(response.data, {
            'token': Token.objects.get(user=user).key,
            'username': 'jane',
            'email': 'jane@example.com',
            'user_id': user.id,
        })

    def test_registration_creates_profile_with_type(self):
        self.payload['type'] = 'business'
        self.client.post(self.url, self.payload, format='json')
        profile = Profile.objects.get(user__username='jane')
        self.assertEqual(profile.type, Profile.BUSINESS)

    def test_password_is_stored_hashed(self):
        self.client.post(self.url, self.payload, format='json')
        user = User.objects.get(username='jane')
        self.assertNotEqual(user.password, 'asdasd')
        self.assertTrue(user.check_password('asdasd'))

    def test_short_password_is_accepted(self):
        self.payload['password'] = self.payload['repeated_password'] = 'a'
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mismatched_passwords_return_400(self):
        self.payload['repeated_password'] = 'other'
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('repeated_password', response.data)
        self.assertFalse(User.objects.filter(username='jane').exists())

    def test_duplicate_username_returns_400(self):
        User.objects.create_user(username='jane', email='x@example.com')
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email_ignores_case(self):
        User.objects.create_user(username='other', email='JANE@example.com')
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_unknown_type_returns_400(self):
        self.payload['type'] = 'admin'
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)

    def test_missing_fields_return_400(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in self.payload:
            self.assertIn(field, response.data)

    def test_stale_token_header_does_not_block_registration(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token deadbeef')
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_email_returns_400(self):
        self.payload['email'] = 'not-an-email'
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
