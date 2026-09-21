from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.filters import StrictOrderingFilter
from core.mixins import ActionConfigMixin
from profile_app.api.permissions import IsCustomerUser
from reviews_app.api.filters import ReviewFilter
from reviews_app.api.permissions import IsReviewer
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review


class ReviewViewSet(ActionConfigMixin,
                    mixins.ListModelMixin,
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
    action_serializers = {'partial_update': ReviewUpdateSerializer}

    def perform_create(self, serializer):
        """Store the requesting customer as the reviewer."""
        serializer.save(reviewer=self.request.user)
