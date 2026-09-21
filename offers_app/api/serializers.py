from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

OFFER_TYPES = [value for value, _ in OfferDetail.TYPE_CHOICES]


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full package with all its fields."""

    features = serializers.ListField(
        child=serializers.CharField(max_length=255),
    )

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type',
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Package reference with a relative URL, used in the offer list."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """Return the relative path the list format expects."""
        return f'/offerdetails/{obj.id}/'


class OfferDetailAbsoluteLinkSerializer(OfferDetailLinkSerializer):
    """Package reference with an absolute URL, used on a single offer."""

    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail',
    )


class UserDetailsSerializer(serializers.ModelSerializer):
    """Name of the offer's creator, shown in the offer list."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Single offer with absolute package links and minimum values."""

    details = OfferDetailAbsoluteLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time',
        ]


class OfferListSerializer(OfferRetrieveSerializer):
    """Offer list entry with relative package links and creator name."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)

    class Meta(OfferRetrieveSerializer.Meta):
        fields = OfferRetrieveSerializer.Meta.fields + ['user_details']


class OfferWriteSerializer(serializers.ModelSerializer):
    """Creates and updates an offer together with its packages."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """Demand all three types on create, unique types on update."""
        types = [detail.get('offer_type') for detail in value]
        if self.instance is None and sorted(types) != sorted(OFFER_TYPES):
            raise serializers.ValidationError(
                'An offer needs exactly one basic, standard and premium '
                'detail.'
            )
        if None in types or len(set(types)) != len(types):
            raise serializers.ValidationError(
                'Every detail needs its own offer_type.'
            )
        if self.instance is not None:
            self.check_types_exist(types)
        return value

    def check_types_exist(self, types):
        """Reject a package type the offer does not have."""
        existing = set(
            self.instance.details.values_list('offer_type', flat=True),
        )
        missing = sorted(set(types) - existing)
        if missing:
            raise serializers.ValidationError(
                f'This offer has no {missing[0]} detail.'
            )

    @transaction.atomic
    def create(self, validated_data):
        """Create the offer and its packages in basic to premium order."""
        details = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        details.sort(key=lambda d: OFFER_TYPES.index(d['offer_type']))
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the offer, then each sent package by its offer_type."""
        details = validated_data.pop('details', [])
        instance = super().update(instance, validated_data)
        for detail in details:
            instance.details.filter(
                offer_type=detail.pop('offer_type'),
            ).update(**detail)
        return instance
