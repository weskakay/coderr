from decimal import ROUND_HALF_UP, Decimal

from rest_framework import serializers


class BaseInfoSerializer(serializers.Serializer):
    """Turns the aggregated numbers into the public statistics."""

    review_count = serializers.IntegerField()
    average_rating = serializers.SerializerMethodField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()

    def get_average_rating(self, stats):
        """Round the average half up to one decimal, 0 without reviews."""
        if not stats['review_count']:
            return 0
        average = Decimal(stats['rating_total']) / stats['review_count']
        return float(average.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
