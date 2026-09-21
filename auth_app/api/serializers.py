from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from profile_app.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates the signup payload and creates user plus profile.

    The Django password validators are not applied here on purpose,
    see the README.
    """

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), lookup='iexact'),
        ],
    )
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=Profile.TYPE_CHOICES,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'repeated_password', 'type',
        ]

    def validate(self, attrs):
        """Reject a signup whose passwords differ."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create the user with a hashed password and its profile."""
        validated_data.pop('repeated_password')
        profile_type = validated_data.pop('type')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, type=profile_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Validates the login payload."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
