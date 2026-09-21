import django_filters

from core.filters import IntegerFilter
from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """Query filters of the review list, empty parameters are ignored."""

    business_user_id = IntegerFilter(field_name='business_user_id')
    reviewer_id = IntegerFilter(field_name='reviewer_id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
