from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.utils import create_offer
from profile_app.models import Profile
from profile_app.tests.utils import create_user


class OfferFilterTests(APITestCase):
    """Covers filters, search and ordering of GET /api/offers/."""

    def setUp(self):
        self.url = reverse('offer-list')
        self.max = create_user('max', Profile.BUSINESS)
        self.eva = create_user('eva', Profile.BUSINESS)
        self.cheap = create_offer(
            self.max, 'Logo design', prices=(10, 20, 30), days=(2, 4, 6),
        )
        self.pricey = create_offer(
            self.eva, 'Website', prices=(300, 400, 500), days=(8, 9, 10),
            description='Shop with logo upload',
        )

    def titles(self, params):
        """Return the titles the list returns for the given parameters."""
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [entry['title'] for entry in response.data['results']]

    def test_creator_id(self):
        self.assertEqual(self.titles({'creator_id': self.eva.id}),
                         ['Website'])

    def test_min_price(self):
        self.assertEqual(self.titles({'min_price': 100}), ['Website'])
        self.assertEqual(len(self.titles({'min_price': 10})), 2)

    def test_max_delivery_time(self):
        self.assertEqual(self.titles({'max_delivery_time': 5}),
                         ['Logo design'])
        self.assertEqual(len(self.titles({'max_delivery_time': 8})), 2)

    def test_search_covers_title_and_description(self):
        self.assertEqual(len(self.titles({'search': 'logo'})), 2)
        self.assertEqual(self.titles({'search': 'shop'}), ['Website'])

    def test_ordering_by_min_price(self):
        self.assertEqual(self.titles({'ordering': 'min_price'}),
                         ['Logo design', 'Website'])
        self.assertEqual(self.titles({'ordering': '-min_price'}),
                         ['Website', 'Logo design'])

    def test_ordering_by_updated_at(self):
        self.cheap.save()
        self.assertEqual(self.titles({'ordering': 'updated_at'}),
                         ['Website', 'Logo design'])
        self.assertEqual(self.titles({'ordering': '-updated_at'}),
                         ['Logo design', 'Website'])

    def test_empty_parameters_are_ignored(self):
        params = {
            'creator_id': '', 'search': '', 'ordering': '', 'page': 1,
            'max_delivery_time': '', 'min_price': '',
        }
        self.assertEqual(len(self.titles(params)), 2)

    def test_combined_filters_keep_count_right(self):
        response = self.client.get(
            self.url, {'creator_id': self.max.id, 'search': 'logo'},
        )
        self.assertEqual(response.data['count'], 1)

    def test_invalid_numbers_return_400(self):
        for params in [{'min_price': 'abc'}, {'creator_id': 'x'},
                       {'max_delivery_time': '1.5'}]:
            response = self.client.get(self.url, params)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, params,
            )

    def test_unknown_ordering_returns_400(self):
        for value in ['title', 'foo', 'min_price,-user']:
            response = self.client.get(self.url, {'ordering': value})
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, value,
            )

    def test_single_offer_ignores_list_parameters(self):
        self.client.force_authenticate(self.max)
        url = reverse('offer-detail', args=[self.cheap.id])
        for params in [{'search': 'zzz'}, {'creator_id': 'abc'}]:
            response = self.client.get(url, params)
            self.assertEqual(response.status_code, status.HTTP_200_OK, params)
