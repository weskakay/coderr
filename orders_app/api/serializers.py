from rest_framework import serializers

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

    The view looks the package up and passes it to save() as
    offer_detail, so a missing package becomes a 404, not a 400.
    """

    offer_detail_id = serializers.IntegerField(write_only=True, min_value=1)

    class Meta(OrderSerializer.Meta):
        fields = ORDER_FIELDS + ['offer_detail_id']

    def create(self, validated_data):
        """Copy the package data into a new order."""
        detail = validated_data['offer_detail']
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
