from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from profile_app.models import Profile

GUESTS = [
    {
        'username': 'andrey',
        'password': 'asdasd',
        'email': 'andrey@example.com',
        'type': Profile.CUSTOMER,
    },
    {
        'username': 'kevin',
        'password': 'asdasd24',
        'email': 'kevin@example.com',
        'type': Profile.BUSINESS,
    },
]


class Command(BaseCommand):
    """Creates the two guest accounts the frontend logs in with."""

    help = 'Create or reset the customer and business guest accounts.'

    def handle(self, *args, **options):
        """Seed every guest, safe to run more than once."""
        for guest in GUESTS:
            self.seed_guest(guest)

    @transaction.atomic
    def seed_guest(self, guest):
        """Create the guest or reset its password and profile type."""
        user, created = User.objects.get_or_create(
            username=guest['username'],
            defaults={'email': guest['email']},
        )
        user.set_password(guest['password'])
        user.save()
        Profile.objects.update_or_create(
            user=user,
            defaults={'type': guest['type']},
        )
        action = 'Created' if created else 'Reset'
        self.stdout.write(f'{action} guest {user.username} ({guest["type"]}).')
