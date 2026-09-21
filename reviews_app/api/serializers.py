from rest_framework import serializers

from profile_app.api.permissions import has_profile_type
from profile_app.models import Profile
from reviews_app.models import Review

REVIEW_FIELDS = [
    'id', 'business_user', 'reviewer', 'rating', 'description',
    'created_at', 'updated_at',
]
EDITABLE_FIELDS = {'rating', 'description'}


class ReviewSerializer(serializers.ModelSerializer):
    """Review with its author taken from the request."""

    class Meta:
        model = Review
        fields = REVIEW_FIELDS
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate_business_user(self, value):
        """Only business users can be reviewed."""
        if not has_profile_type(value, Profile.BUSINESS):
            raise serializers.ValidationError(
                'This user is not a business user.'
            )
        return value


class ReviewUpdateSerializer(ReviewSerializer):
    """Changes rating and description of a review and nothing else."""

    class Meta(ReviewSerializer.Meta):
        read_only_fields = [
            f for f in REVIEW_FIELDS if f not in EDITABLE_FIELDS
        ]

    def validate(self, attrs):
        """Reject any field besides rating and description."""
        extra = sorted(set(self.initial_data) - EDITABLE_FIELDS)
        if extra:
            raise serializers.ValidationError(
                {field: 'This field cannot be changed.' for field in extra}
            )
        return attrs
