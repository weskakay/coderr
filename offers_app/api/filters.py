import django_filters
from django import forms
from rest_framework import filters
from rest_framework.exceptions import ValidationError

from offers_app.models import Offer


class IntegerFilter(django_filters.NumberFilter):
    """Number filter that only accepts whole numbers."""

    field_class = forms.IntegerField


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


class StrictOrderingFilter(filters.OrderingFilter):
    """Ordering filter that rejects unknown fields instead of ignoring them."""

    def get_ordering(self, request, queryset, view):
        """Raise a 400 for fields outside the view's ordering_fields."""
        terms = request.query_params.get(self.ordering_param, '').split(',')
        unknown = [
            term for term in terms
            if term.strip() and term.strip().lstrip('-')
            not in view.ordering_fields
        ]
        if unknown:
            raise ValidationError({'ordering': f'Unknown field: {unknown[0]}'})
        return super().get_ordering(request, queryset, view)
