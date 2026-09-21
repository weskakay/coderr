from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.api.permissions import IsProfileOwnerOrReadOnly
from profile_app.api.serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    ProfileSerializer,
)
from profile_app.models import Profile


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """GET and PATCH /api/profile/{pk}/, where pk is the user id.

    The owner check runs in get_object(), so a stranger gets 403 before
    the body is validated.
    """

    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'user'
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'patch', 'head', 'options']


class BusinessProfileListView(generics.ListAPIView):
    """GET /api/profiles/business/ lists all business profiles."""

    queryset = Profile.objects.filter(
        type=Profile.BUSINESS,
    ).select_related('user')
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """GET /api/profiles/customer/ lists all customer profiles."""

    queryset = Profile.objects.filter(
        type=Profile.CUSTOMER,
    ).select_related('user')
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
