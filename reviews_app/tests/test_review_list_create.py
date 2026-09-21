from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import Profile
from profile_app.tests.utils import create_user
from reviews_app.models import Review
from reviews_app.tests.utils import create_review

REVIEW_FIELDS = [
    'id', 'business_user', 'reviewer', 'rating', 'description',
    'created_at', 'updated_at',
]


class ReviewListTests(APITestCase):
    """Covers GET /api/reviews/ with filters and ordering."""

    def setUp(self):
        self.url = reverse('review-list')
        self.max = create_user('max', Profile.BUSINESS)
        self.eva = create_user('eva', Profile.BUSINESS)
        self.jane = create_user('jane')
        self.tom = create_user('tom')
        self.low = create_review(self.max, self.jane, rating=2)
        self.high = create_review(self.eva, self.jane, rating=5)
        self.mid = create_review(self.max, self.tom, rating=3)
        self.space_out_timestamps([self.low, self.high, self.mid])
        self.client.force_authenticate(self.jane)

    def space_out_timestamps(self, reviews):
        """Give the reviews updated_at values one hour apart, oldest first."""
        start = timezone.now() - timedelta(days=1)
        for hours, review in enumerate(reviews):
            Review.objects.filter(pk=review.pk).update(
                updated_at=start + timedelta(hours=hours),
            )

    def ids(self, params=None):
        """Return the review ids the list returns for the parameters."""
        response = self.client.get(self.url, params or {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [review['id'] for review in response.data]

    def test_plain_list_newest_first(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.data, list)
        self.assertEqual(list(response.data[0]), REVIEW_FIELDS)
        self.assertEqual(self.ids(),
                         [self.mid.id, self.high.id, self.low.id])

    def test_filter_by_business_user_and_reviewer(self):
        self.assertEqual(self.ids({'business_user_id': self.max.id}),
                         [self.mid.id, self.low.id])
        self.assertEqual(self.ids({'reviewer_id': self.jane.id}),
                         [self.high.id, self.low.id])

    def test_ordering_by_rating_and_updated_at(self):
        self.assertEqual(self.ids({'ordering': 'rating'}),
                         [self.low.id, self.mid.id, self.high.id])
        self.assertEqual(self.ids({'ordering': '-rating'}),
                         [self.high.id, self.mid.id, self.low.id])
        self.assertEqual(self.ids({'ordering': 'updated_at'}),
                         [self.low.id, self.high.id, self.mid.id])

    def test_query_the_frontend_sends(self):
        params = {'business_user_id': self.max.id, 'ordering': '-updated_at'}
        self.assertEqual(self.ids(params), [self.mid.id, self.low.id])
        params = {'reviewer_id': self.jane.id, 'ordering': '-updated_at'}
        self.assertEqual(self.ids(params), [self.high.id, self.low.id])

    def test_empty_parameters_are_ignored(self):
        params = {'business_user_id': '', 'reviewer_id': '', 'ordering': ''}
        self.assertEqual(len(self.ids(params)), 3)

    def test_invalid_parameters_return_400(self):
        for params in [{'business_user_id': 'x'}, {'reviewer_id': '1.5'},
                       {'reviewer_id': '99999999999999999999'},
                       {'ordering': 'description'}, {'ordering': '--rating'}]:
            response = self.client.get(self.url, params)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, params,
            )

    def test_anonymous_gets_401(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCreateTests(APITestCase):
    """Covers POST /api/reviews/."""

    def setUp(self):
        self.url = reverse('review-list')
        self.business = create_user('max', Profile.BUSINESS)
        self.customer = create_user('jane')
        self.payload = {
            'business_user': self.business.id, 'rating': 4,
            'description': 'All good!',
        }

    def post(self, user, payload):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.post(self.url, payload, format='json')

    def test_customer_creates_review(self):
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(response.data), REVIEW_FIELDS)
        self.assertEqual(response.data['reviewer'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.business.id)
        self.assertEqual(response.data['rating'], 4)

    def test_reviewer_in_body_is_ignored(self):
        other = create_user('tom')
        payload = dict(self.payload, reviewer=other.id)
        response = self.post(self.customer, payload)
        self.assertEqual(response.data['reviewer'], self.customer.id)

    def test_second_review_for_same_business_returns_403(self):
        self.post(self.customer, self.payload)
        response = self.post(self.customer, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)

    def test_other_customer_may_review_same_business(self):
        self.post(self.customer, self.payload)
        response = self.post(create_user('tom'), self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_business_user_gets_403(self):
        response = self.post(create_user('eva', Profile.BUSINESS),
                             self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_data_returns_400(self):
        for change in [{'rating': 0}, {'rating': 6}, {'rating': 'x'},
                       {'description': ''}, {'business_user': 9999},
                       {'business_user': self.customer.id}]:
            response = self.post(self.customer, dict(self.payload, **change))
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, change,
            )

    def test_missing_fields_return_400(self):
        response = self.post(self.customer, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in self.payload:
            self.assertIn(field, response.data)
