from django.apps import AppConfig


class OffersAppConfig(AppConfig):
    """App holding offers and their three packages."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offers_app'
