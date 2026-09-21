from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import Profile
from profile_app.tests.utils import create_user
from reviews_app.models import Review
from reviews_app.tests.utils import create_review


class ReviewUpdateTests(APITestCase):
    """Covers PATCH /api/reviews/{id}/."""

    def setUp(self):
        self.business = create_user('max', Profile.BUSINESS)
        self.author = create_user('jane')
        self.review = create_review(self.business, self.author)
        self.url = reverse('review-detail', args=[self.review.id])

    def patch(self, user, payload):
        """Send the payload as the given user."""
        self.client.force_authenticate(user)
        return self.client.patch(self.url, payload, format='json')

    def test_author_changes_rating_and_description(self):
        payload = {'rating': 5, 'description': 'Even better!'}
        response = self.patch(self.author, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Even better!')
        self.assertEqual(response.data['business_user'], self.business.id)

    def test_other_fields_return_400(self):
        other = create_user('eva', Profile.BUSINESS)
        payload = {'rating': 5, 'business_user': other.id}
        response = self.patch(self.author, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user', response.data)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_empty_body_returns_400(self):
        before = self.review.updated_at
        response = self.patch(self.author, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.review.refresh_from_db()
        self.assertEqual(self.review.updated_at, before)

    def test_invalid_rating_returns_400(self):
        response = self.patch(self.author, {'rating': 9})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stranger_gets_403_before_validation(self):
        response = self.patch(create_user('tom'), {'rating': 9})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewed_business_gets_403(self):
        response = self.patch(self.business, {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        response = self.client.patch(self.url, {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_review_returns_404(self):
        self.url = reverse('review-detail', args=[9999])
        response = self.patch(self.author, {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_parameters_do_not_hide_the_review(self):
        self.client.force_authenticate(self.author)
        response = self.client.patch(
            f'{self.url}?business_user_id=x', {'rating': 5}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_head_and_put_do_not_exist(self):
        self.client.force_authenticate(self.author)
        for method in ['get', 'head', 'put']:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(
                response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                method,
            )


class ReviewDeleteTests(APITestCase):
    """Covers DELETE /api/reviews/{id}/."""

    def setUp(self):
        self.author = create_user('jane')
        self.review = create_review(
            create_user('max', Profile.BUSINESS), self.author,
        )
        self.url = reverse('review-detail', args=[self.review.id])

    def test_author_deletes_review(self):
        self.client.force_authenticate(self.author)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.exists())

    def test_stranger_gets_403(self):
        self.client.force_authenticate(create_user('tom'))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.exists())

    def test_anonymous_gets_401(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_review_returns_404(self):
        self.client.force_authenticate(self.author)
        response = self.client.delete(reverse('review-detail', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
