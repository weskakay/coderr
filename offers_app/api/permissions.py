from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOfferOwnerOrReadOnly(BasePermission):
    """Anyone may read an offer, only its creator may change it."""

    message = 'Only the creator of this offer may change it.'

    def has_object_permission(self, request, view, obj):
        """Allow reads, compare the creator with the user for changes."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
