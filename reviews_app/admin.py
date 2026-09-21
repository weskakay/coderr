from django.contrib import admin

from reviews_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin list of all reviews, filterable by rating."""

    list_display = ['reviewer', 'business_user', 'rating', 'updated_at']
    list_filter = ['rating']
    search_fields = [
        'description', 'reviewer__username', 'business_user__username',
    ]
    list_select_related = ['reviewer', 'business_user']
