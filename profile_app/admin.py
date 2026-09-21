from django.contrib import admin

from profile_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin list of all profiles, filterable by account type."""

    list_display = ['user', 'type', 'location', 'created_at']
    list_filter = ['type']
    search_fields = ['user__username', 'user__email', 'location']
    list_select_related = ['user']
