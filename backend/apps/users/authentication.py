from collections.abc import Mapping

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


def token_matches_password_version(user, claims: Mapping[str, object]) -> bool:
    issued_at = claims.get("iat")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool):
        return False
    return issued_at >= int(user.password_changed_at.timestamp())


class PasswordChangedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not token_matches_password_version(user, validated_token.payload):
            raise AuthenticationFailed(
                "La sesión fue invalidada porque cambió la contraseña.",
                code="password_changed",
            )
        return user
