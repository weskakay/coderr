from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    build_auth_response,
)


class RegistrationView(generics.CreateAPIView):
    """POST /api/registration/ creates an account and returns a token.

    No authentication runs here, so a stale token sent by the frontend
    cannot block the request.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


class LoginView(APIView):
    """POST /api/login/ returns a token for valid credentials.

    Ignores any token header for the same reason as registration.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Log an existing user in by username."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_auth_response(user))
