from django.test import TestCase

from profile_app.models import Profile
from profile_app.tests.utils import create_user


class ProfileModelTests(TestCase):
    """Covers defaults and text output of the profile model."""

    def test_str_shows_username_and_type(self):
        user = create_user('max', Profile.BUSINESS)
        self.assertEqual(str(user.profile), 'max (business)')

    def test_text_fields_default_to_empty_string(self):
        profile = create_user('jane').profile
        for field in ['location', 'tel', 'description', 'working_hours']:
            self.assertEqual(getattr(profile, field), '', field)

    def test_deleting_user_deletes_profile(self):
        user = create_user('jane')
        user.delete()
        self.assertFalse(Profile.objects.exists())
