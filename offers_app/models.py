from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Offer(models.Model):
    """Service a business user offers in three packages."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'offer'
        verbose_name_plural = 'offers'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """One of the three packages of an offer."""

    BASIC = 'basic'
    STANDARD = 'standard'
    PREMIUM = 'premium'
    TYPE_CHOICES = [
        (BASIC, 'Basic'),
        (STANDARD, 'Standard'),
        (PREMIUM, 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
    )
    title = models.CharField(max_length=255)
    # -1 means unlimited revisions.
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = 'offer detail'
        verbose_name_plural = 'offer details'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['offer', 'offer_type'],
                name='unique_offer_type_per_offer',
            ),
        ]

    def __str__(self):
        return f'{self.offer.title} ({self.offer_type})'
