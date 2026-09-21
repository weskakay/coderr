from rest_framework import serializers
from rest_framework.exceptions import NotFound

from core.filters import MAX_INTEGER
from offers_app.models import OfferDetail
from orders_app.models import Order

ORDER_FIELDS = [
    'id', 'customer_user', 'business_user', 'title', 'revisions',
    'delivery_time_in_days', 'price', 'features', 'offer_type', 'status',
    'created_at', 'updated_at',
]


class OrderSerializer(serializers.ModelSerializer):
    """Read only representation of an order."""

    class Meta:
        model = Order
        fields = ORDER_FIELDS
        read_only_fields = ORDER_FIELDS


class OrderCreateSerializer(OrderSerializer):
    """Creates an order from a package id.

    A malformed id is a 400, an id without a package is a 404.
    """

    offer_detail_id = serializers.IntegerField(
        write_only=True, min_value=1, max_value=MAX_INTEGER,
    )

    class Meta(OrderSerializer.Meta):
        fields = ORDER_FIELDS + ['offer_detail_id']

    def validate_offer_detail_id(self, value):
        """Return the package behind the id, or answer 404."""
        detail = OfferDetail.objects.select_related('offer').filter(
            pk=value,
        ).first()
        if detail is None:
            raise NotFound('No package matches this id.')
        return detail

    def create(self, validated_data):
        """Copy the package data into a new order."""
        detail = validated_data['offer_detail_id']
        return Order.objects.create(
            customer_user=validated_data['customer_user'],
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )


class OrderStatusSerializer(OrderSerializer):
    """Changes the status of an order and nothing else."""

    class Meta(OrderSerializer.Meta):
        read_only_fields = [f for f in ORDER_FIELDS if f != 'status']

    def validate(self, attrs):
        """Reject any field besides status, and a missing status."""
        extra = sorted(set(self.initial_data) - {'status'})
        if extra:
            raise serializers.ValidationError(
                {field: 'This field cannot be changed.' for field in extra}
            )
        if 'status' not in attrs:
            raise serializers.ValidationError(
                {'status': 'This field is required.'}
            )
        return attrs
