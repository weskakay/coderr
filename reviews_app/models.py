from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Rating a customer gives a business user, one per pair.

    Reviews go with a deleted account: a review of a missing business or
    by a missing reviewer can no longer be attributed to anyone.
    """

    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='written_reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['business_user', 'reviewer'],
                name='one_review_per_business_and_reviewer',
            ),
        ]

    def __str__(self):
        return (
            f'{self.reviewer.username} on {self.business_user.username}: '
            f'{self.rating}'
        )
