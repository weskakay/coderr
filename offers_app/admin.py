from django.contrib import admin

from offers_app.models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Edit the three packages right on the offer page."""

    model = OfferDetail
    extra = 0
    min_num = 3
    max_num = 3
    can_delete = False


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin list of all offers with their packages inline."""

    list_display = ['title', 'user', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    list_select_related = ['user']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin list of all packages, filterable by type."""

    list_display = [
        'title', 'offer', 'offer_type', 'price', 'delivery_time_in_days',
    ]
    list_filter = ['offer_type']
    search_fields = ['title', 'offer__title']
    list_select_related = ['offer']
