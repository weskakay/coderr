from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from profile_app.models import Profile
from profile_app.tests.utils import create_user
from reviews_app.models import Review
from reviews_app.tests.utils import create_review


class ReviewModelTests(TestCase):
    """Covers text output, uniqueness and deletion of reviews."""

    def setUp(self):
        self.business = create_user('max', Profile.BUSINESS)
        self.reviewer = create_user('jane')
        self.review = create_review(self.business, self.reviewer)

    def test_str(self):
        self.assertEqual(str(self.review), 'jane on max: 4')

    def test_one_review_per_pair(self):
        with self.assertRaises(IntegrityError):
            create_review(self.business, self.reviewer)

    def test_reviews_go_with_a_deleted_user(self):
        self.reviewer.delete()
        self.assertFalse(Review.objects.exists())


class ReviewAdminTests(TestCase):
    """Checks that the review admin pages open for staff."""

    def setUp(self):
        admin = User.objects.create_superuser('admin', 'a@example.com', 'pw')
        self.client.force_login(admin)
        self.review = create_review(
            create_user('max', Profile.BUSINESS), create_user('jane'),
        )

    def test_pages_open(self):
        urls = [
            reverse('admin:reviews_app_review_changelist'),
            reverse('admin:reviews_app_review_change', args=[self.review.pk]),
        ]
        for url in urls:
            response = self.client.get(url, {'q': 'good'})
            self.assertEqual(response.status_code, 200, url)
