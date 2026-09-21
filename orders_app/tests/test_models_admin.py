from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from orders_app.tests.utils import create_order
from profile_app.models import Profile
from profile_app.tests.utils import create_user


class OrderModelTests(TestCase):
    """Covers text output and delete protection of orders."""

    def setUp(self):
        self.customer = create_user('jane')
        self.business = create_user('max', Profile.BUSINESS)
        self.order = create_order(self.customer, self.business)

    def test_str(self):
        self.assertEqual(str(self.order), 'Logo Design (in_progress)')

    def test_users_with_orders_cannot_be_deleted(self):
        for user in [self.customer, self.business]:
            with self.assertRaises(ProtectedError):
                user.delete()


class OrderAdminTests(TestCase):
    """Checks that the order admin pages open for staff."""

    def setUp(self):
        admin = User.objects.create_superuser('admin', 'a@example.com', 'pw')
        self.client.force_login(admin)
        self.order = create_order(
            create_user('jane'), create_user('max', Profile.BUSINESS),
        )

    def test_pages_open(self):
        urls = [
            reverse('admin:orders_app_order_changelist'),
            reverse('admin:orders_app_order_change', args=[self.order.pk]),
        ]
        for url in urls:
            response = self.client.get(url, {'q': 'logo'})
            self.assertEqual(response.status_code, 200, url)
