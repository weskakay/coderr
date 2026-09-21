import django_filters

from core.filters import IntegerFilter
from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """Query filters of the offer list.

    min_price and max_delivery_time work on the values annotated in the
    view's queryset. Empty parameters are ignored.
    """

    creator_id = IntegerFilter(field_name='user_id')
    min_price = django_filters.NumberFilter(
        field_name='min_price',
        lookup_expr='gte',
    )
    max_delivery_time = IntegerFilter(
        field_name='min_delivery_time',
        lookup_expr='lte',
    )

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']
