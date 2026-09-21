from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin list of all orders, filterable by status and package type."""

    list_display = [
        'title', 'customer_user', 'business_user', 'price', 'status',
        'created_at',
    ]
    list_filter = ['status', 'offer_type']
    search_fields = [
        'title', 'customer_user__username', 'business_user__username',
    ]
    list_select_related = ['customer_user', 'business_user']
