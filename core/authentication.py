from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class OptionalTokenAuthentication(TokenAuthentication):
    """Token authentication that treats an invalid token like no token.

    The frontend sends its stored token with every request. After a
    database reset that token is stale, which would turn public endpoints
    into 401. Protected endpoints still answer 401 through their
    permissions.
    """

    def authenticate(self, request):
        """Return the user of a valid token, None for a missing or bad one."""
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None
