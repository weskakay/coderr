from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """App holding registration and login."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
