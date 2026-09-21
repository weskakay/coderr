from django.contrib.auth.models import User
from django.db import models

from offers_app.models import OfferDetail


class Order(models.Model):
    """Order of one package, with the package data copied at order time.

    Both users are protected: an account with orders cannot be deleted,
    so neither side ever loses its order history.
    """

    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    customer_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='business_orders',
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(
        max_length=10,
        choices=OfferDetail.TYPE_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'
