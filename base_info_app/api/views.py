from django.db.models import Count, Sum
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from base_info_app.api.serializers import BaseInfoSerializer
from offers_app.models import Offer
from profile_app.models import Profile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """GET /api/base-info/ returns public platform statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return the statistics built from the current numbers."""
        return Response(BaseInfoSerializer(self.collect_numbers()).data)

    def collect_numbers(self):
        """Count reviews, business profiles and offers in the database."""
        numbers = Review.objects.aggregate(
            review_count=Count('id'), rating_total=Sum('rating'),
        )
        numbers['business_profile_count'] = Profile.objects.filter(
            type=Profile.BUSINESS,
        ).count()
        numbers['offer_count'] = Offer.objects.count()
        return numbers
