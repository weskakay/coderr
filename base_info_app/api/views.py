from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, Sum
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profile_app.models import Profile
from reviews_app.models import Review


def rounded_average(total, count):
    """Return total / count rounded half up to one decimal, 0 without data."""
    if not count:
        return 0
    average = Decimal(total) / Decimal(count)
    return float(average.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


class BaseInfoView(APIView):
    """GET /api/base-info/ returns public platform statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Count reviews, business profiles and offers, average the ratings."""
        reviews = Review.objects.aggregate(
            count=Count('id'), total=Sum('rating'),
        )
        return Response({
            'review_count': reviews['count'],
            'average_rating': rounded_average(
                reviews['total'], reviews['count'],
            ),
            'business_profile_count': Profile.objects.filter(
                type=Profile.BUSINESS,
            ).count(),
            'offer_count': Offer.objects.count(),
        })
