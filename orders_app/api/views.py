from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from orders_app.api.permissions import IsOrderBusinessUser
from orders_app.api.serializers import (
    CompletedOrderCountSerializer,
    OrderCountSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)
from orders_app.models import Order
from profile_app.api.permissions import IsCustomerUserOrReadOnly
from profile_app.models import Profile


class OrderListCreateView(generics.ListCreateAPIView):
    """GET and POST /api/orders/, only customers may order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerUserOrReadOnly]

    def get_queryset(self):
        """Only the orders the user takes part in, as customer or business."""
        user = self.request.user
        return super().get_queryset().filter(
            Q(customer_user=user) | Q(business_user=user),
        )

    def get_serializer_class(self):
        """Take a package id when ordering, show full orders otherwise."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Order the package for the requesting customer."""
        serializer.save(customer_user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH and DELETE /api/orders/{id}/.

    The specification has no GET on a single order, so GET, HEAD and PUT
    are left out of http_method_names.
    """

    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAuthenticated, IsOrderBusinessUser]
    http_method_names = ['patch', 'delete', 'options']

    def get_permissions(self):
        """Staff may delete, the order's business user may change status."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()


class OrderCountView(generics.RetrieveAPIView):
    """GET /api/order-count/{id}/ counts a business user's open orders."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrderCountSerializer
    counted_status = Order.IN_PROGRESS
    response_key = 'order_count'

    def get_object(self):
        """Return the count, or 404 if there is no such business user."""
        business_user_id = self.kwargs['business_user_id']
        get_object_or_404(
            Profile, user_id=business_user_id, type=Profile.BUSINESS,
        )
        count = Order.objects.filter(
            business_user_id=business_user_id, status=self.counted_status,
        ).count()
        return {self.response_key: count}


class CompletedOrderCountView(OrderCountView):
    """GET /api/completed-order-count/{id}/ counts completed orders."""

    serializer_class = CompletedOrderCountSerializer
    counted_status = Order.COMPLETED
    response_key = 'completed_order_count'
