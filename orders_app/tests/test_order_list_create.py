from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.utils import create_offer
from orders_app.models import Order
from orders_app.tests.utils import create_order
from profile_app.models import Profile
from profile_app.tests.utils import create_user

ORDER_FIELDS = [
    'id', 'customer_user', 'business_user', 'title', 'revisions',
    'delivery_time_in_days', 'price', 'features', 'offer_type', 'status',
    'created_at', 'updated_at',
]


class OrderListTests(APITestCase):
    """Covers GET /api/orders/."""

    def setUp(self):
        self.url = reverse('order-list')
        self.customer = create_user('jane')
        self.business = create_user('max', Profile.BUSINESS)
        self.other = create_user('eva', Profile.BUSINESS)
        self.mine = create_order(self.customer, self.business)
        create_order(create_user('tom'), self.other)

    def ids_for(self, user):
        """Return the order ids the list shows to the given user."""
        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [order['id'] for order in response.data]

    def test_customer_and_business_see_their_order(self):
        self.assertEqual(self.ids_for(self.customer), [self.mine.id])
        self.assertEqual(self.ids_for(self.business), [self.mine.id])

    def test_stranger_sees_only_own_orders(self):
        theirs = Order.objects.get(business_user=self.other)
        self.assertEqual(self.ids_for(self.other), [theirs.id])

    def test_list_is_plain_array_with_order_fields(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(self.url)
        self.assertIsInstance(response.data, list)
        self.assertEqual(list(response.data[0]), ORDER_FIELDS)
        self.assertEqual(response.json()[0]['price'], 150)

    def test_anonymous_gets_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreateTests(APITestCase):
    """Covers POST /api/orders/."""

    def setUp(self):
        self.url = reverse('order-list')
        self.customer = create_user('jane')
        self.business = create_user('max', Profile.BUSINESS)
        offer = create_offer(self.business)
        self.detail = offer.details.get(offer_type='standard')
        self.payload = {'offer_detail_id': self.detail.id}

    def post(self, user, payload):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.post(self.url, payload, format='json')

    def test_customer_orders_a_package(self):
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(response.data), ORDER_FIELDS)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['title'], 'Standard Design')
        self.assertEqual(response.data['offer_type'], 'standard')
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.json()['price'], 200)

    def test_order_keeps_data_when_package_changes(self):
        response = self.post(self.customer, self.payload)
        self.detail.price = 999
        self.detail.title = 'Changed'
        self.detail.save()
        order = Order.objects.get(pk=response.data['id'])
        self.assertEqual(order.price, 200)
        self.assertEqual(order.title, 'Standard Design')

    def test_client_values_for_read_only_fields_are_ignored(self):
        payload = dict(
            self.payload, status='completed', price=1,
            customer_user=self.business.id,
        )
        response = self.post(self.customer, payload)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.json()['price'], 200)

    def test_user_without_profile_gets_403(self):
        self.customer.profile.delete()
        self.customer.refresh_from_db()
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_user_gets_403(self):
        response = self.post(self.business, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_user_gets_403_even_for_unknown_package(self):
        response = self.post(self.business, {'offer_detail_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.post(self.url, {'offer_detail_id': 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_package_returns_404(self):
        response = self.post(self.customer, {'offer_detail_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Order.objects.exists())

    def test_missing_or_invalid_id_returns_400(self):
        for payload in [{}, {'offer_detail_id': 'abc'},
                        {'offer_detail_id': 0}, {'offer_detail_id': None}]:
            response = self.post(self.customer, payload)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, payload,
            )
