# coding=utf-8

from django.utils.timezone import now
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from user.models import AuthToken


class TokenAuthentication(BaseAuthentication):
    keyword = 'Token'
    model = None

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = AuthToken.objects.select_related('user').get(key=key)
        except AuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if token.expire < now():
            raise exceptions.AuthenticationFailed('Token is expired, please re-login.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword


class SessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        return (user, None)