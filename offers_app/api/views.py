from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.filters import StrictOrderingFilter
from core.mixins import ActionConfigMixin
from offers_app.api.filters import OfferFilter
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsOfferOwner
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail
from profile_app.api.permissions import IsBusinessUser


class OfferViewSet(ActionConfigMixin, viewsets.ModelViewSet):
    """List, create, read, update and delete offers.

    The list is public and paginated. Minimum price and delivery time are
    computed in the query, so filtering and sorting by them costs no extra
    queries.
    """

    # Django drops Meta.ordering on aggregated queries, so sort explicitly.
    queryset = Offer.objects.annotate(
        min_price=Min('details__price'),
        min_delivery_time=Min('details__delivery_time_in_days'),
    ).select_related('user').prefetch_related('details').order_by(
        '-updated_at',
    )
    serializer_class = OfferListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OfferPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, StrictOrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    action_permissions = {
        'list': [AllowAny],
        'create': [IsAuthenticated, IsBusinessUser],
        'partial_update': [IsAuthenticated, IsOfferOwner],
        'destroy': [IsAuthenticated, IsOfferOwner],
    }
    action_serializers = {
        'retrieve': OfferRetrieveSerializer,
        'create': OfferWriteSerializer,
        'partial_update': OfferWriteSerializer,
    }

    def perform_create(self, serializer):
        """Store the requesting user as the creator."""
        serializer.save(user=self.request.user)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """GET /api/offerdetails/{id}/ returns one full package."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
