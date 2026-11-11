from collections.abc import Mapping

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


PASSWORD_VERSION_CLAIM = "password_version"


class PasswordVersionRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token[PASSWORD_VERSION_CLAIM] = user.password_changed_at.isoformat()
        return token


def token_matches_password_version(user, claims: Mapping[str, object]) -> bool:
    issued_at = claims.get("iat")
    if not isinstance(issued_at, int) or isinstance(issued_at, bool):
        return False
    if PASSWORD_VERSION_CLAIM in claims:
        return (
            claims[PASSWORD_VERSION_CLAIM] == user.password_changed_at.isoformat()
            and issued_at >= int(user.password_changed_at.timestamp())
        )
    # Legacy JWTs have only second precision. Reject the ambiguous second;
    # new logins carry the exact version, also copied to their access tokens.
    return issued_at >= user.password_changed_at.timestamp()


class PasswordChangedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not token_matches_password_version(user, validated_token.payload):
            raise AuthenticationFailed(
                "La sesión fue invalidada porque cambió la contraseña.",
                code="password_changed",
            )
        return user
