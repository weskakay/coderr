from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from profile_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin list of all profiles, filterable by account type."""

    list_display = ['user', 'type', 'location', 'created_at']
    list_filter = ['type']
    search_fields = ['user__username', 'user__email', 'location']
    list_select_related = ['user']


class ProfileInline(admin.StackedInline):
    """Profile on the user page, so users added here get one too."""

    model = Profile
    can_delete = False
    readonly_fields = ['uploaded_at']


class UserWithProfileAdmin(UserAdmin):
    """Django's user admin with the profile attached."""

    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserWithProfileAdmin)
