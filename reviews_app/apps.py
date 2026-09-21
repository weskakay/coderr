from django.apps import AppConfig


class ReviewsAppConfig(AppConfig):
    """App holding customer reviews of business users."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews_app'
