from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


class KeycloakJWTAuthentication(JWTAuthentication):
    """
    Accept externally-issued JWTs (e.g. Keycloak access tokens) that don't carry
    SimpleJWT's `token_type` claim, while still validating signature/expiry.
    """

    _ALLOWED_EXTERNAL_TYPES = {'bearer', 'access', 'jwt'}

    @classmethod
    def _ensure_access_token(cls, token: UntypedToken) -> None:
        payload = token.payload
        token_type = payload.get('token_type')
        if token_type is not None:
            if token_type != 'access':
                raise InvalidToken({'detail': 'Token is not an access token.', 'code': 'token_not_valid'})
            return

        external_type = payload.get('typ')
        if isinstance(external_type, str) and external_type.lower() in cls._ALLOWED_EXTERNAL_TYPES:
            return

        raise InvalidToken({'detail': 'Token is not an access token.', 'code': 'token_not_valid'})

    def get_validated_token(self, raw_token):
        try:
            validated_token = UntypedToken(raw_token)
        except TokenError as exc:
            raise InvalidToken({'detail': str(exc), 'code': 'token_not_valid'})

        self._ensure_access_token(validated_token)
        return validated_token
