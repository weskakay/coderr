from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import OfferDetail
from orders_app.api.permissions import IsOrderBusinessUser
from orders_app.api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)
from orders_app.models import Order
from profile_app.api.permissions import IsCustomerUser
from profile_app.models import Profile


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """List, create, update and delete orders.

    There is no retrieve action, so GET /api/orders/{id}/ does not exist.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    action_permissions = {
        'create': [IsAuthenticated, IsCustomerUser],
        'partial_update': [IsAuthenticated, IsOrderBusinessUser],
        'destroy': [IsAuthenticated, IsAdminUser],
    }
    action_serializers = {
        'create': OrderCreateSerializer,
        'partial_update': OrderStatusSerializer,
    }

    def get_permissions(self):
        """Return the permissions of the current action."""
        classes = self.action_permissions.get(
            self.action, self.permission_classes,
        )
        return [permission() for permission in classes]

    def get_serializer_class(self):
        """Return the serializer of the current action."""
        return self.action_serializers.get(self.action, self.serializer_class)

    def get_queryset(self):
        """Limit the list to orders the user takes part in."""
        if self.action != 'list':
            return self.queryset
        user = self.request.user
        return self.queryset.filter(
            Q(customer_user=user) | Q(business_user=user),
        )

    def perform_create(self, serializer):
        """Look the package up and order it for the requesting customer."""
        detail = get_object_or_404(
            OfferDetail.objects.select_related('offer'),
            pk=serializer.validated_data['offer_detail_id'],
        )
        serializer.save(customer_user=self.request.user, offer_detail=detail)


class OrderCountView(APIView):
    """GET /api/order-count/{id}/ counts a business user's open orders."""

    permission_classes = [IsAuthenticated]
    counted_status = Order.IN_PROGRESS
    response_key = 'order_count'

    def get(self, request, business_user_id):
        """Return the count, or 404 if there is no such business user."""
        get_object_or_404(
            Profile, user_id=business_user_id, type=Profile.BUSINESS,
        )
        count = Order.objects.filter(
            business_user_id=business_user_id, status=self.counted_status,
        ).count()
        return Response({self.response_key: count})


class CompletedOrderCountView(OrderCountView):
    """GET /api/completed-order-count/{id}/ counts completed orders."""

    counted_status = Order.COMPLETED
    response_key = 'completed_order_count'
