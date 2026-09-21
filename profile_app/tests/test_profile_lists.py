from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import Profile
from profile_app.tests.utils import create_user

BUSINESS_FIELDS = [
    'user', 'username', 'first_name', 'last_name', 'file', 'location',
    'tel', 'description', 'working_hours', 'type',
]
CUSTOMER_FIELDS = [
    'user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at',
    'type',
]


class ProfileListTests(APITestCase):
    """Covers GET /api/profiles/business/ and /api/profiles/customer/."""

    def setUp(self):
        self.business = create_user('max', Profile.BUSINESS)
        self.customer = create_user('jane', Profile.CUSTOMER)
        self.business_url = reverse('business-profile-list')
        self.customer_url = reverse('customer-profile-list')

    def test_business_list_contains_only_business_profiles(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(list(response.data[0]), BUSINESS_FIELDS)
        self.assertEqual(response.data[0]['user'], self.business.id)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_customer_list_contains_only_customer_profiles(self):
        self.client.force_authenticate(self.business)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(list(response.data[0]), CUSTOMER_FIELDS)
        self.assertEqual(response.data[0]['user'], self.customer.id)
        self.assertIsNotNone(response.data[0]['uploaded_at'])

    def test_lists_are_plain_arrays_without_pagination(self):
        self.client.force_authenticate(self.business)
        for url in (self.business_url, self.customer_url):
            response = self.client.get(url)
            self.assertIsInstance(response.data, list)

    def test_empty_text_fields_are_strings_not_null(self):
        self.client.force_authenticate(self.business)
        entry = self.client.get(self.business_url).data[0]
        for field in ['first_name', 'last_name', 'location', 'tel',
                      'description', 'working_hours']:
            self.assertEqual(entry[field], '', field)
        entry = self.client.get(self.customer_url).data[0]
        for field in ['first_name', 'last_name']:
            self.assertEqual(entry[field], '', field)

    def test_anonymous_gets_401(self):
        for url in (self.business_url, self.customer_url):
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED,
            )

    def test_post_is_not_allowed(self):
        self.client.force_authenticate(self.business)
        response = self.client.post(self.business_url, {})
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
        )
