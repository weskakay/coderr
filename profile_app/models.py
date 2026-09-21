from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    """Extra data and account type of a user."""

    CUSTOMER = 'customer'
    BUSINESS = 'business'
    TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (BUSINESS, 'Business'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.ImageField(upload_to='profiles/', blank=True)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    # Starts at signup and moves forward with every new picture.
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
        ordering = ['user_id']

    def __str__(self):
        return f'{self.user.username} ({self.type})'
