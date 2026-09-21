from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    """Allows changes to an offer by its creator only."""

    message = 'Only the creator of this offer may change it.'

    def has_object_permission(self, request, view, obj):
        """Compare the offer's creator with the requesting user."""
        return obj.user_id == request.user.id
