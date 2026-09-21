from django.urls import path

from offers_app.api.views import (
    OfferDetailRetrieveView,
    OfferDetailView,
    OfferListCreateView,
)

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list'),
    path('offers/<id:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path(
        'offerdetails/<id:pk>/',
        OfferDetailRetrieveView.as_view(),
        name='offerdetail-detail',
    ),
]
