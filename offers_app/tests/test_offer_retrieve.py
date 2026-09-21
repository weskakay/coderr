from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.utils import create_offer
from profile_app.models import Profile
from profile_app.tests.utils import create_user

RETRIEVE_FIELDS = [
    'id', 'user', 'title', 'image', 'description', 'created_at',
    'updated_at', 'details', 'min_price', 'min_delivery_time',
]


class OfferRetrieveTests(APITestCase):
    """Covers GET /api/offers/{id}/ and GET /api/offerdetails/{id}/."""

    def setUp(self):
        self.business = create_user('max', Profile.BUSINESS)
        self.customer = create_user('jane')
        self.offer = create_offer(self.business, prices=(50, 80, 120))
        self.url = reverse('offer-detail', args=[self.offer.id])

    def test_logged_in_user_gets_offer_with_absolute_links(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data), RETRIEVE_FIELDS)
        first = self.offer.details.first()
        self.assertEqual(response.data['details'][0], {
            'id': first.id,
            'url': f'http://testserver/api/offerdetails/{first.id}/',
        })
        self.assertEqual(response.data['min_price'], 50)
        self.assertEqual(response.data['min_delivery_time'], 5)
        self.assertEqual(response.data['user'], self.business.id)

    def test_anonymous_gets_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_offer_returns_404(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse('offer-detail', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_is_not_allowed(self):
        self.client.force_authenticate(self.business)
        response = self.client.put(self.url, {}, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_offerdetail_returns_full_package(self):
        detail = self.offer.details.get(offer_type='standard')
        self.client.force_authenticate(self.customer)
        response = self.client.get(
            reverse('offerdetail-detail', args=[detail.id]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': detail.id, 'title': 'Standard Design', 'revisions': 2,
            'delivery_time_in_days': 7, 'price': 80,
            'features': ['Logo Design', 'Business Card'],
            'offer_type': 'standard',
        })

    def test_offerdetail_anonymous_gets_401(self):
        detail = self.offer.details.first()
        url = reverse('offerdetail-detail', args=[detail.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offerdetail_unknown_returns_404(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse('offerdetail-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
