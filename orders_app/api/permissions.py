from rest_framework.permissions import BasePermission


class IsOrderBusinessUser(BasePermission):
    """Allows changes to an order by its business user only."""

    message = 'Only the business user of this order may change it.'

    def has_object_permission(self, request, view, obj):
        """Compare the order's business user with the requesting user."""
        return obj.business_user_id == request.user.id
