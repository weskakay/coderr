from django.urls import include, path
from rest_framework.routers import SimpleRouter

from reviews_app.api.views import ReviewViewSet

router = SimpleRouter()
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
