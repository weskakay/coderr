from django.apps import AppConfig


class OrdersAppConfig(AppConfig):
    """App holding orders placed on offer packages."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders_app'
