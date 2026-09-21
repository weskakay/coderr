from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """Allows changes to a review by its author only."""

    message = 'Only the author of this review may change it.'

    def has_object_permission(self, request, view, obj):
        """Compare the review's author with the requesting user."""
        return obj.reviewer_id == request.user.id
