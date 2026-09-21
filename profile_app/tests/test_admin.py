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

    def test_user_added_in_admin_gets_a_profile(self):
        payload = {
            'username': 'newbie', 'usable_password': 'true',
            'password1': 'Str0ng-pass-99', 'password2': 'Str0ng-pass-99',
            'profile-TOTAL_FORMS': '1', 'profile-INITIAL_FORMS': '0',
            'profile-0-type': 'business',
        }
        response = self.client.post(reverse('admin:auth_user_add'), payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newbie')
        self.assertEqual(user.profile.type, 'business')

    def test_user_page_shows_the_profile(self):
        url = reverse('admin:auth_user_change', args=[self.profile.user_id])
        response = self.client.get(url)
        self.assertContains(response, 'name="profile-0-type"')
