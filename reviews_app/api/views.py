from django.db import IntegrityError, transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from core.filters import StrictOrderingFilter
from profile_app.api.permissions import IsCustomerUser
from reviews_app.api.filters import ReviewFilter
from reviews_app.api.permissions import IsReviewer
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review


class ReviewViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """List, create, update and delete reviews.

    There is no retrieve action, so GET /api/reviews/{id}/ does not exist.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, StrictOrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    action_permissions = {
        'create': [IsAuthenticated, IsCustomerUser],
        'partial_update': [IsAuthenticated, IsReviewer],
        'destroy': [IsAuthenticated, IsReviewer],
    }

    def get_permissions(self):
        """Return the permissions of the current action."""
        classes = self.action_permissions.get(
            self.action, self.permission_classes,
        )
        return [permission() for permission in classes]

    def get_serializer_class(self):
        """Use the restricted serializer for updates."""
        if self.action == 'partial_update':
            return ReviewUpdateSerializer
        return self.serializer_class

    def filter_queryset(self, queryset):
        """Apply filters and ordering to the list only."""
        if self.action != 'list':
            return queryset
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        """Save the review, a second one for the same business is a 403."""
        try:
            with transaction.atomic():
                serializer.save(reviewer=self.request.user)
        except IntegrityError:
            raise PermissionDenied(
                'You have already reviewed this business user.'
            )
