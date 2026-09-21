from django.urls import path

from orders_app.api.views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderDetailView,
    OrderListCreateView,
)

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<id:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path(
        'order-count/<id:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count',
    ),
    path(
        'completed-order-count/<id:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count',
    ),
]
