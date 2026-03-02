from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


class KeycloakJWTAuthentication(JWTAuthentication):
    """
    Accept externally-issued JWTs (e.g. Keycloak access tokens) that don't carry
    SimpleJWT's `token_type` claim, while still validating signature/expiry.
    """

    def get_validated_token(self, raw_token):
        try:
            return UntypedToken(raw_token)
        except TokenError as exc:
            raise InvalidToken({'detail': str(exc), 'code': 'token_not_valid'})

