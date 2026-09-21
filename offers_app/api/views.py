from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from core.filters import StrictOrderingFilter
from offers_app.api.filters import OfferFilter
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsOfferOwnerOrReadOnly
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail
from profile_app.api.permissions import IsBusinessUserOrReadOnly

# Minimum price and delivery time are computed in the query, so filtering
# and sorting by them costs no extra queries. Django drops Meta.ordering on
# aggregated queries, so sort explicitly.
OFFERS = Offer.objects.annotate(
    min_price=Min('details__price'),
    min_delivery_time=Min('details__delivery_time_in_days'),
).select_related('user').prefetch_related('details').order_by('-updated_at')


class OfferListCreateView(generics.ListCreateAPIView):
    """GET /api/offers/ is public and paginated, POST is for business users."""

    queryset = OFFERS
    serializer_class = OfferListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUserOrReadOnly]
    pagination_class = OfferPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, StrictOrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        """Take all three packages when creating, list them as links."""
        if self.request.method == 'POST':
            return OfferWriteSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Store the requesting user as the creator."""
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PATCH and DELETE /api/offers/{id}/, changes by the creator only."""

    queryset = OFFERS
    serializer_class = OfferRetrieveSerializer
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """Answer a PATCH with all packages written out."""
        if self.request.method == 'PATCH':
            return OfferWriteSerializer
        return self.serializer_class


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """GET /api/offerdetails/{id}/ returns one full package."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
