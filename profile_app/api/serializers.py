from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from profile_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Full profile, merging the user's name and email into it."""

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name',
        max_length=150,
        allow_blank=True,
        required=False,
    )
    last_name = serializers.CharField(
        source='user.last_name',
        max_length=150,
        allow_blank=True,
        required=False,
    )
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]
        read_only_fields = ['user', 'type', 'created_at']

    def validate_email(self, value):
        """Reject an email that another account already uses."""
        taken = User.objects.filter(email__iexact=value).exclude(
            pk=self.instance.user_id,
        )
        if taken.exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Save name and email on the user, everything else on the profile."""
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        if 'file' in validated_data:
            instance.uploaded_at = timezone.now()
        return super().update(instance, validated_data)


class ProfileListSerializer(serializers.ModelSerializer):
    """Shared read only user fields of the profile lists."""

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True,
    )
    last_name = serializers.CharField(source='user.last_name', read_only=True)


class BusinessProfileListSerializer(ProfileListSerializer):
    """Entry of the business profile list."""

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        ]


class CustomerProfileListSerializer(ProfileListSerializer):
    """Entry of the customer profile list."""

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type',
        ]
