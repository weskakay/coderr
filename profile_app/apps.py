from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    """App holding user profiles and their account type."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_app'
