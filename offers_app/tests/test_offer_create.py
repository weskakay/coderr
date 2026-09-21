from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from offers_app.tests.utils import detail_payload, offer_payload
from profile_app.models import Profile
from profile_app.tests.utils import create_user

DETAIL_FIELDS = [
    'id', 'title', 'revisions', 'delivery_time_in_days', 'price',
    'features', 'offer_type',
]


class OfferCreateTests(APITestCase):
    """Covers POST /api/offers/."""

    def setUp(self):
        self.url = reverse('offer-list')
        self.business = create_user('max', Profile.BUSINESS)
        self.customer = create_user('jane', Profile.CUSTOMER)
        self.payload = offer_payload()

    def post(self, user, payload):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.post(self.url, payload, format='json')

    def test_business_creates_offer_with_full_details(self):
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            list(response.data),
            ['id', 'title', 'image', 'description', 'details'],
        )
        details = response.data['details']
        self.assertEqual([list(d) for d in details], [DETAIL_FIELDS] * 3)
        self.assertEqual([d['price'] for d in details], [100, 200, 500])
        offer = Offer.objects.get(pk=response.data['id'])
        self.assertEqual(offer.user, self.business)

    def test_details_are_stored_basic_to_premium(self):
        self.payload['details'].reverse()
        response = self.post(self.business, self.payload)
        types = [d['offer_type'] for d in response.data['details']]
        self.assertEqual(types, ['basic', 'standard', 'premium'])

    def test_price_as_string_and_unlimited_revisions(self):
        self.payload['details'][0].update(price='99.50', revisions=-1)
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['details'][0]['price'], 99.5)
        self.assertEqual(response.data['details'][0]['revisions'], -1)

    def test_customer_gets_403(self):
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Offer.objects.exists())

    def test_user_without_profile_gets_403(self):
        self.customer.profile.delete()
        self.customer.refresh_from_db()
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_two_details_return_400(self):
        self.payload['details'].pop()
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)
        self.assertFalse(Offer.objects.exists())

    def test_duplicate_type_returns_400(self):
        self.payload['details'][2] = detail_payload('basic')
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_details_return_400(self):
        del self.payload['details']
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_detail_values_return_400(self):
        for field, value in [('delivery_time_in_days', 0),
                             ('revisions', -2), ('price', -1),
                             ('offer_type', 'gold'), ('features', 'text')]:
            payload = offer_payload()
            payload['details'][0][field] = value
            response = self.post(self.business, payload)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, field,
            )

    def test_missing_title_returns_400(self):
        del self.payload['title']
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
