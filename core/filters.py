import django_filters
from django import forms
from rest_framework import filters
from rest_framework.exceptions import ValidationError


# Largest value a database integer column holds.
MAX_INTEGER = 2 ** 63 - 1


class BoundedIntegerField(forms.IntegerField):
    """Integer form field limited to what the database can store."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('min_value', -MAX_INTEGER)
        kwargs.setdefault('max_value', MAX_INTEGER)
        super().__init__(*args, **kwargs)


class IntegerFilter(django_filters.NumberFilter):
    """Number filter that only accepts whole numbers of database size."""

    field_class = BoundedIntegerField


class StrictOrderingFilter(filters.OrderingFilter):
    """Ordering filter that rejects unknown fields instead of ignoring them."""

    def get_ordering(self, request, queryset, view):
        """Raise a 400 for fields outside the view's ordering_fields."""
        terms = request.query_params.get(self.ordering_param, '').split(',')
        unknown = [
            term for term in terms
            if term.strip() and term.strip().removeprefix('-')
            not in view.ordering_fields
        ]
        if unknown:
            raise ValidationError({'ordering': f'Unknown field: {unknown[0]}'})
        return super().get_ordering(request, queryset, view)
