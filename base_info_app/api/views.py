from django.db.models import Count, Sum
from rest_framework import generics
from rest_framework.permissions import AllowAny

from base_info_app.api.serializers import BaseInfoSerializer
from offers_app.models import Offer
from profile_app.models import Profile
from reviews_app.models import Review


class BaseInfoView(generics.RetrieveAPIView):
    """GET /api/base-info/ returns public platform statistics."""

    permission_classes = [AllowAny]
    serializer_class = BaseInfoSerializer

    def get_object(self):
        """Return the numbers the statistics are built from."""
        numbers = Review.objects.aggregate(
            review_count=Count('id'), rating_total=Sum('rating'),
        )
        numbers['business_profile_count'] = Profile.objects.filter(
            type=Profile.BUSINESS,
        ).count()
        numbers['offer_count'] = Offer.objects.count()
        return numbers
