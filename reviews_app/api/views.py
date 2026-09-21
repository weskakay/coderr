from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.filters import StrictOrderingFilter
from profile_app.api.permissions import IsCustomerUserOrReadOnly
from reviews_app.api.filters import ReviewFilter
from reviews_app.api.permissions import IsReviewer
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review


class ReviewListCreateView(generics.ListCreateAPIView):
    """GET and POST /api/reviews/, only customers may create."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomerUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, StrictOrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']

    def perform_create(self, serializer):
        """Store the requesting customer as the reviewer."""
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH and DELETE /api/reviews/{id}/, for the author only.

    The specification has no GET on a single review, so GET, HEAD and PUT
    are left out of http_method_names.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    http_method_names = ['patch', 'delete', 'options']
