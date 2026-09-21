from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.utils import create_offer
from profile_app.models import Profile
from profile_app.tests.utils import create_user

LIST_FIELDS = [
    'id', 'user', 'title', 'image', 'description', 'created_at',
    'updated_at', 'details', 'min_price', 'min_delivery_time',
    'user_details',
]


class OfferListTests(APITestCase):
    """Covers GET /api/offers/ without query parameters."""

    def setUp(self):
        self.url = reverse('offer-list')
        self.business = create_user(
            'max', Profile.BUSINESS, first_name='Max', last_name='Doe',
        )

    def test_list_is_public_and_paginated(self):
        offer = create_offer(self.business)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(response.data), ['count', 'next', 'previous', 'results'],
        )
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], offer.id)

    def test_entry_has_list_format(self):
        offer = create_offer(self.business)
        entry = self.client.get(self.url).data['results'][0]
        self.assertEqual(list(entry), LIST_FIELDS)
        detail_ids = [d.id for d in offer.details.all()]
        self.assertEqual(entry['details'], [
            {'id': pk, 'url': f'/offerdetails/{pk}/'} for pk in detail_ids
        ])
        self.assertEqual(entry['user_details'], {
            'first_name': 'Max', 'last_name': 'Doe', 'username': 'max',
        })

    def test_minimum_values_are_numbers(self):
        create_offer(self.business, prices=(50.5, 20, 90), days=(9, 3, 4))
        entry = self.client.get(self.url).json()['results'][0]
        self.assertEqual(entry['min_price'], 20)
        self.assertIsInstance(entry['min_price'], float)
        self.assertEqual(entry['min_delivery_time'], 3)

    def test_six_offers_per_page(self):
        for number in range(8):
            create_offer(self.business, title=f'Offer {number}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 8)
        self.assertEqual(len(response.data['results']), 6)
        self.assertIn('page=2', response.data['next'])
        second = self.client.get(self.url, {'page': 2})
        self.assertEqual(len(second.data['results']), 2)

    def test_page_size_parameter(self):
        for number in range(3):
            create_offer(self.business, title=f'Offer {number}')
        response = self.client.get(self.url, {'page_size': 2})
        self.assertEqual(len(response.data['results']), 2)

    def test_newest_offer_comes_first(self):
        create_offer(self.business, title='Old')
        create_offer(self.business, title='New')
        results = self.client.get(self.url).data['results']
        self.assertEqual(results[0]['title'], 'New')

    def test_query_count_does_not_grow_with_offers(self):
        create_offer(self.business)
        with CaptureQueriesContext(connection) as one:
            self.client.get(self.url)
        for number in range(4):
            create_offer(self.business, title=f'Offer {number}')
        with CaptureQueriesContext(connection) as five:
            self.client.get(self.url)
        self.assertEqual(len(one), len(five))

    def test_post_by_anonymous_is_401(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
