import shutil
import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from offers_app.tests.utils import create_offer, detail_payload
from profile_app.models import Profile
from profile_app.tests.utils import create_user, make_image

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class OfferUpdateTests(APITestCase):
    """Covers PATCH /api/offers/{id}/."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.addClassCleanup(shutil.rmtree, MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.owner = create_user('max', Profile.BUSINESS)
        self.stranger = create_user('eva', Profile.BUSINESS)
        self.offer = create_offer(self.owner)
        self.url = reverse('offer-detail', args=[self.offer.id])
        self.detail_ids = [d.id for d in self.offer.details.all()]

    def patch(self, user, payload, fmt='json'):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.patch(self.url, payload, format=fmt)

    def test_owner_updates_one_package_by_type(self):
        basic = detail_payload('basic', price=120, days=6)
        basic.update(title='Basic Updated', features=['Flyer'])
        payload = {'title': 'Updated', 'details': [basic]}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated')
        details = response.data['details']
        self.assertEqual([d['id'] for d in details], self.detail_ids)
        self.assertEqual(details[0]['title'], 'Basic Updated')
        self.assertEqual(details[0]['features'], ['Flyer'])
        self.assertEqual(details[1]['price'], 200)

    def test_package_fields_can_be_sent_partially(self):
        payload = {'details': [{'offer_type': 'premium', 'price': 999}]}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        premium = response.data['details'][2]
        self.assertEqual(premium['price'], 999)
        self.assertEqual(premium['title'], 'Premium Design')

    def test_frontend_edit_with_all_details_and_foreign_ids(self):
        other = create_offer(self.stranger)
        details = [detail_payload(t, price=p) for t, p in
                   zip(['basic', 'standard', 'premium'], [11, 22, 33])]
        for detail, foreign in zip(details, other.details.all()):
            detail['id'] = foreign.id
        payload = {'title': 'T', 'description': 'D', 'details': details}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data['details']
        self.assertEqual([d['id'] for d in result], self.detail_ids)
        self.assertEqual([d['price'] for d in result], [11, 22, 33])
        prices = [d.price for d in other.details.all()]
        self.assertEqual(prices, [100, 200, 500])

    def test_update_moves_updated_at(self):
        before = self.offer.updated_at
        self.patch(self.owner, {'description': 'New text'})
        self.offer.refresh_from_db()
        self.assertGreater(self.offer.updated_at, before)

    def test_image_upload_as_multipart(self):
        response = self.patch(self.owner, {'image': make_image()}, 'multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['image'].startswith('http://'))
        self.assertIn('/media/offers/', response.data['image'])

    def test_package_without_type_returns_400(self):
        payload = {'details': [{'price': 1}]}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_type_returns_400(self):
        payload = {'details': [{'offer_type': 'gold', 'price': 1}]}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_type_the_offer_lacks_returns_400(self):
        self.offer.details.filter(offer_type='premium').delete()
        payload = {'details': [{'offer_type': 'premium', 'price': 1}]}
        response = self.patch(self.owner, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_stranger_gets_403_before_validation(self):
        payload = {'details': [{'offer_type': 'gold'}]}
        response = self.patch(self.stranger, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.patch(self.url, {'title': 'x'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_offer_returns_404(self):
        self.url = reverse('offer-detail', args=[9999])
        response = self.patch(self.owner, {'title': 'x'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferDeleteTests(APITestCase):
    """Covers DELETE /api/offers/{id}/."""

    def setUp(self):
        self.owner = create_user('max', Profile.BUSINESS)
        self.offer = create_offer(self.owner)
        self.url = reverse('offer-detail', args=[self.offer.id])

    def test_owner_deletes_offer_and_packages(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.exists())

    def test_stranger_gets_403(self):
        self.client.force_authenticate(create_user('eva', Profile.BUSINESS))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.exists())

    def test_anonymous_gets_401(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_offer_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(reverse('offer-detail', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
