import shutil
import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import Profile
from profile_app.tests.utils import create_user, make_image, make_text_file

MEDIA_ROOT = tempfile.mkdtemp()

PROFILE_FIELDS = [
    'user', 'username', 'first_name', 'last_name', 'file', 'location',
    'tel', 'description', 'working_hours', 'type', 'email', 'created_at',
]
TEXT_FIELDS = [
    'first_name', 'last_name', 'location', 'tel', 'description',
    'working_hours',
]


def profile_url(user_id):
    """Return the detail URL of the profile owned by user_id."""
    return reverse('profile-detail', kwargs={'pk': user_id})


class ProfileRetrieveTests(APITestCase):
    """Covers GET /api/profile/{pk}/."""

    def setUp(self):
        self.owner = create_user('max', Profile.BUSINESS)
        self.other = create_user('jane')

    def test_anonymous_gets_401(self):
        response = self.client.get(profile_url(self.owner.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_any_user_can_read_a_profile(self):
        self.client.force_authenticate(self.other)
        response = self.client.get(profile_url(self.owner.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data), PROFILE_FIELDS)
        self.assertEqual(response.data['user'], self.owner.id)
        self.assertEqual(response.data['username'], 'max')
        self.assertEqual(response.data['type'], 'business')
        self.assertEqual(response.data['email'], 'max@example.com')

    def test_empty_text_fields_are_strings_not_null(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(profile_url(self.owner.id))
        for field in TEXT_FIELDS:
            self.assertEqual(response.data[field], '', field)
        self.assertIsNone(response.data['file'])

    def test_unknown_user_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(profile_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_huge_id_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/profile/99999999999999999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_profile_returns_404(self):
        admin = create_user('admin')
        admin.profile.delete()
        self.client.force_authenticate(self.owner)
        response = self.client.get(profile_url(admin.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_is_not_allowed(self):
        self.client.force_authenticate(self.owner)
        response = self.client.put(profile_url(self.owner.id), {})
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ProfileUpdateTests(APITestCase):
    """Covers PATCH /api/profile/{pk}/."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.addClassCleanup(shutil.rmtree, MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.owner = create_user('max', Profile.BUSINESS)
        self.other = create_user('jane')
        self.url = profile_url(self.owner.id)

    def test_owner_updates_user_and_profile_fields(self):
        self.client.force_authenticate(self.owner)
        payload = {
            'first_name': 'Max', 'last_name': 'Mustermann', 'tel': '98765',
            'location': 'Berlin', 'description': 'Updated',
            'working_hours': '10-18', 'email': 'new@business.de',
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data), PROFILE_FIELDS)
        for field, value in payload.items():
            self.assertEqual(response.data[field], value, field)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.email, 'new@business.de')

    def test_partial_update_keeps_other_fields(self):
        Profile.objects.filter(user=self.owner).update(location='Berlin')
        self.client.force_authenticate(self.owner)
        response = self.client.patch(self.url, {'tel': '1'}, format='json')
        self.assertEqual(response.data['location'], 'Berlin')
        self.assertEqual(response.data['tel'], '1')

    def test_owner_uploads_picture_as_multipart(self):
        old_stamp = self.owner.profile.uploaded_at
        self.client.force_authenticate(self.owner)
        payload = {'file': make_image(), 'location': 'Hamburg'}
        response = self.client.patch(self.url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['file'].startswith('http://'))
        self.assertIn('/media/profiles/', response.data['file'])
        self.owner.profile.refresh_from_db()
        self.assertGreater(self.owner.profile.uploaded_at, old_stamp)

    def test_non_image_file_returns_400(self):
        self.client.force_authenticate(self.owner)
        payload = {'file': make_text_file()}
        response = self.client.patch(self.url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_type_and_username_are_read_only(self):
        self.client.force_authenticate(self.owner)
        payload = {'type': 'customer', 'username': 'hacker'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.data['type'], 'business')
        self.assertEqual(response.data['username'], 'max')

    def test_email_of_another_account_returns_400(self):
        self.client.force_authenticate(self.owner)
        payload = {'email': 'JANE@example.com'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_keeping_own_email_is_allowed(self):
        self.client.force_authenticate(self.owner)
        payload = {'email': 'max@example.com'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_null_text_field_returns_400(self):
        self.client.force_authenticate(self.owner)
        payload = {'location': None}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_gets_401(self):
        response = self.client.patch(self.url, {'tel': '1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stranger_gets_403(self):
        self.client.force_authenticate(self.other)
        response = self.client.patch(self.url, {'tel': '1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.owner.profile.refresh_from_db()
        self.assertEqual(self.owner.profile.tel, '')

    def test_stranger_with_invalid_body_gets_403_not_400(self):
        self.client.force_authenticate(self.other)
        payload = {'email': 'not-an-email'}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_profile_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            profile_url(9999), {'tel': '1'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
