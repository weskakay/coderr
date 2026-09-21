from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from offers_app.models import OfferDetail
from offers_app.tests.utils import create_offer, detail_payload
from profile_app.models import Profile
from profile_app.tests.utils import create_user


class OfferModelTests(TestCase):
    """Covers text output and constraints of the offer models."""

    def setUp(self):
        self.offer = create_offer(create_user('max', Profile.BUSINESS))

    def test_str(self):
        detail = self.offer.details.get(offer_type='basic')
        self.assertEqual(str(self.offer), 'Graphic design')
        self.assertEqual(str(detail), 'Graphic design (basic)')

    def test_type_is_unique_per_offer(self):
        with self.assertRaises(IntegrityError):
            OfferDetail.objects.create(
                offer=self.offer, **detail_payload('basic'),
            )


class OfferAdminTests(TestCase):
    """Checks that the offer admin pages open for staff."""

    def setUp(self):
        admin = User.objects.create_superuser('admin', 'a@example.com', 'pw')
        self.client.force_login(admin)
        self.offer = create_offer(create_user('max', Profile.BUSINESS))

    def test_pages_open(self):
        urls = [
            reverse('admin:offers_app_offer_changelist'),
            reverse('admin:offers_app_offer_change', args=[self.offer.pk]),
            reverse('admin:offers_app_offerdetail_changelist'),
        ]
        for url in urls:
            response = self.client.get(url, {'q': 'design'})
            self.assertEqual(response.status_code, 200, url)

    def test_offer_page_keeps_exactly_three_packages(self):
        url = reverse('admin:offers_app_offer_change', args=[self.offer.pk])
        response = self.client.get(url)
        self.assertContains(response, 'name="details-MIN_NUM_FORMS" value="3"')
        self.assertContains(response, 'name="details-MAX_NUM_FORMS" value="3"')
        self.assertNotContains(response, 'details-0-DELETE')
