from django.urls import path

from reviews_app.api.views import ReviewDetailView, ReviewListCreateView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path(
        'reviews/<id:pk>/',
        ReviewDetailView.as_view(),
        name='review-detail',
    ),
]
