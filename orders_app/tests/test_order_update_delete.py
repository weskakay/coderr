from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from orders_app.tests.utils import create_order
from profile_app.models import Profile
from profile_app.tests.utils import create_user


class OrderUpdateTests(APITestCase):
    """Covers PATCH /api/orders/{id}/."""

    def setUp(self):
        self.customer = create_user('jane')
        self.business = create_user('max', Profile.BUSINESS)
        self.order = create_order(self.customer, self.business)
        self.url = reverse('order-detail', args=[self.order.id])

    def patch(self, user, payload):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.patch(self.url, payload, format='json')

    def test_business_user_changes_status(self):
        before = self.order.updated_at
        response = self.patch(self.business, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['id'], self.order.id)
        self.order.refresh_from_db()
        self.assertGreater(self.order.updated_at, before)

    def test_every_status_value_is_accepted(self):
        for value in ['completed', 'cancelled', 'in_progress']:
            response = self.patch(self.business, {'status': value})
            self.assertEqual(response.status_code, status.HTTP_200_OK, value)

    def test_other_fields_return_400(self):
        payload = {'status': 'completed', 'price': 1}
        response = self.patch(self.business, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_invalid_or_missing_status_returns_400(self):
        for payload in [{'status': 'done'}, {}, {'status': None}]:
            response = self.patch(self.business, payload)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, payload,
            )

    def test_customer_of_the_order_gets_403(self):
        response = self.patch(self.customer, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_business_gets_403_before_validation(self):
        other = create_user('eva', Profile.BUSINESS)
        response = self.patch(other, {'status': 'done', 'price': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_multipart_status_change_works(self):
        self.client.force_authenticate(self.business)
        response = self.client.patch(
            self.url, {'status': 'cancelled'}, format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_staff_cannot_change_status(self):
        staff = User.objects.create_user('admin', is_staff=True)
        response = self.patch(staff, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.patch(self.url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_order_returns_404(self):
        self.url = reverse('order-detail', args=[9999])
        response = self.patch(self.business, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_head_and_put_do_not_exist(self):
        self.client.force_authenticate(self.business)
        for method in ['get', 'head', 'put']:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                method,
            )


class OrderDeleteTests(APITestCase):
    """Covers DELETE /api/orders/{id}/."""

    def setUp(self):
        self.business = create_user('max', Profile.BUSINESS)
        self.order = create_order(create_user('jane'), self.business)
        self.url = reverse('order-detail', args=[self.order.id])
        self.staff = User.objects.create_user('admin', is_staff=True)

    def test_staff_deletes_order(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.exists())

    def test_business_user_of_the_order_gets_403(self):
        self.client.force_authenticate(self.business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.exists())

    def test_anonymous_gets_401(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_gets_404_for_unknown_order(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(reverse('order-detail', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
