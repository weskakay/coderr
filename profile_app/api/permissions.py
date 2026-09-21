from rest_framework.permissions import SAFE_METHODS, BasePermission

from profile_app.models import Profile


def has_profile_type(user, profile_type):
    """Tell whether the user has a profile of the given type."""
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.type == profile_type


class IsProfileOwnerOrReadOnly(BasePermission):
    """Anyone may read a profile, only its owner may change it."""

    def has_object_permission(self, request, view, obj):
        """Allow reads, allow writes on the own profile only."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class IsBusinessUser(BasePermission):
    """Allows access to users with a business profile only."""

    message = 'Only business users may do this.'

    def has_permission(self, request, view):
        """Check the account type of the requesting user."""
        return has_profile_type(request.user, Profile.BUSINESS)


class IsCustomerUser(BasePermission):
    """Allows access to users with a customer profile only."""

    message = 'Only customer users may do this.'

    def has_permission(self, request, view):
        """Check the account type of the requesting user."""
        return has_profile_type(request.user, Profile.CUSTOMER)


class IsBusinessUserOrReadOnly(IsBusinessUser):
    """Anyone may read, only business users may create."""

    def has_permission(self, request, view):
        """Allow reads, check the account type for everything else."""
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsCustomerUserOrReadOnly(IsCustomerUser):
    """Anyone may read, only customer users may create."""

    def has_permission(self, request, view):
        """Allow reads, check the account type for everything else."""
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)
