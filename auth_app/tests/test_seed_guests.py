from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from profile_app.models import Profile


class SeedGuestsTests(TestCase):
    """Covers the seed_guests management command."""

    def run_command(self):
        """Run the command with its output swallowed."""
        call_command('seed_guests', stdout=StringIO())

    def test_creates_both_guests_with_their_type(self):
        self.run_command()
        andrey = User.objects.get(username='andrey')
        kevin = User.objects.get(username='kevin')
        self.assertTrue(andrey.check_password('asdasd'))
        self.assertTrue(kevin.check_password('asdasd24'))
        self.assertEqual(andrey.profile.type, Profile.CUSTOMER)
        self.assertEqual(kevin.profile.type, Profile.BUSINESS)

    def test_second_run_creates_no_duplicates(self):
        self.run_command()
        self.run_command()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)

    def test_resets_changed_password_and_type(self):
        self.run_command()
        kevin = User.objects.get(username='kevin')
        kevin.set_password('changed')
        kevin.save()
        Profile.objects.filter(user=kevin).update(type=Profile.CUSTOMER)
        self.run_command()
        kevin.refresh_from_db()
        self.assertTrue(kevin.check_password('asdasd24'))
        self.assertEqual(kevin.profile.type, Profile.BUSINESS)
