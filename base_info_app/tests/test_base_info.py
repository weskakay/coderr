from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.utils import create_offer
from profile_app.models import Profile
from profile_app.tests.utils import create_user
from reviews_app.tests.utils import create_review


class BaseInfoTests(APITestCase):
    """Covers GET /api/base-info/."""

    def setUp(self):
        self.url = reverse('base-info')

    def test_empty_platform_returns_zeros(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'review_count': 0, 'average_rating': 0,
            'business_profile_count': 0, 'offer_count': 0,
        })

    def test_counts_and_rounded_average(self):
        max_ = create_user('max', Profile.BUSINESS)
        create_user('eva', Profile.BUSINESS)
        create_user('jane')
        create_offer(max_)
        create_offer(max_, title='Second')
        for reviewer, rating in [('a', 5), ('b', 4), ('c', 4)]:
            create_review(max_, create_user(reviewer), rating=rating)
        response = self.client.get(self.url)
        self.assertEqual(response.json(), {
            'review_count': 3, 'average_rating': 4.3,
            'business_profile_count': 2, 'offer_count': 2,
        })

    def test_average_rounds_half_up(self):
        business = create_user('max', Profile.BUSINESS)
        for number, rating in enumerate([4, 4, 5, 4]):
            create_review(business, create_user(f'c{number}'), rating=rating)
        response = self.client.get(self.url)
        self.assertEqual(response.json()['average_rating'], 4.3)

    def test_is_public_even_with_a_stale_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token deadbeef')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_is_not_allowed(self):
        response = self.client.post(self.url, {})
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
        )
