from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profile_app.tests.utils import create_user


class ProfileAdminTests(TestCase):
    """Checks that the profile admin pages open for staff."""

    def setUp(self):
        admin = User.objects.create_superuser('admin', 'a@example.com', 'pw')
        self.client.force_login(admin)
        self.profile = create_user('jane').profile

    def test_changelist_with_search_opens(self):
        url = reverse('admin:profile_app_profile_changelist')
        query = {'q': 'jane', 'type__exact': 'customer'}
        response = self.client.get(url, query)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'jane')

    def test_change_page_opens(self):
        url = reverse(
            'admin:profile_app_profile_change', args=[self.profile.pk],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
