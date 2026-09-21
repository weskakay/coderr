from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Anyone may read a profile, only its owner may change it."""

    def has_object_permission(self, request, view, obj):
        """Allow reads, allow writes on the own profile only."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
