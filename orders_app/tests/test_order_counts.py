from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from orders_app.tests.utils import create_order
from profile_app.models import Profile
from profile_app.tests.utils import create_user


class OrderCountTests(APITestCase):
    """Covers GET /api/order-count/ and /api/completed-order-count/."""

    def setUp(self):
        self.customer = create_user('jane')
        self.business = create_user('max', Profile.BUSINESS)
        other = create_user('eva', Profile.BUSINESS)
        for state in [Order.IN_PROGRESS, Order.IN_PROGRESS, Order.COMPLETED,
                      Order.CANCELLED]:
            create_order(self.customer, self.business, state)
        create_order(self.customer, other, Order.IN_PROGRESS)
        self.client.force_authenticate(self.customer)

    def get(self, name, user_id):
        """Call the named count endpoint for the given user id."""
        return self.client.get(reverse(name, args=[user_id]))

    def test_order_count_counts_open_orders(self):
        response = self.get('order-count', self.business.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 2})

    def test_completed_count_counts_completed_orders(self):
        response = self.get('completed-order-count', self.business.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 1})

    def test_business_without_orders_gets_zero(self):
        fresh = create_user('new', Profile.BUSINESS)
        response = self.get('order-count', fresh.id)
        self.assertEqual(response.data, {'order_count': 0})

    def test_unknown_or_customer_id_returns_404(self):
        for name in ['order-count', 'completed-order-count']:
            for user_id in [9999, self.customer.id]:
                response = self.get(name, user_id)
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND, name,
                )

    def test_anonymous_gets_401(self):
        self.client.force_authenticate(None)
        for name in ['order-count', 'completed-order-count']:
            response = self.get(name, self.business.id)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED, name,
            )

    def test_huge_id_returns_404(self):
        response = self.client.get('/api/order-count/99999999999999999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
