from django.urls import include, path
from rest_framework.routers import SimpleRouter

from orders_app.api.views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderViewSet,
)

router = SimpleRouter()
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
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
