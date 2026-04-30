import logging
import os
from functools import cached_property

import jwt
from django.conf import settings
from ninja.security import HttpBearer

logger = logging.getLogger(__name__)

ALLOWED_ALGORITHMS = ["RS256"]
JWT_SET_CACHE_TTL_SECONDS = 3600


class Authentication(HttpBearer):
    def authenticate(self, request, token) -> dict | None:
        """
        Authenticates the incoming request by validating the JWT token.
        """
        if self.bypass_authentication:
            logger.warning("Authentication bypass is enabled.")
            return {"oid": "bypass_object_id", "sub": "bypass_user"}

        request.auth = self._decode(token)
        return request.auth

    def _decode(self, token: str) -> dict | None:
        """
        Decodes and validates the JWT token using the provided RSA key.
        Checks the signature, audience, and issuer claims to ensure the token is valid and intended for this API.
        """
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=ALLOWED_ALGORITHMS,
                audience=self.audience,
                issuer=self.issuers,
            )
            return payload
        except jwt.PyJWKClientError:
            logger.exception("Error fetching JWKS keys from Azure AD.")
        except jwt.ExpiredSignatureError:
            logger.exception("Token is expired")
        except (jwt.InvalidAudienceError, jwt.InvalidIssuerError):
            logger.exception("Invalid claims. Please check the audience and issuer.")
        except jwt.InvalidTokenError:
            logger.exception("Token is invalid")
        except Exception:
            logger.exception("Unable to parse authentication token.")

    @cached_property
    def jwks_client(self) -> jwt.PyJWKClient:
        """
        Creates a PyJWKClient instance for fetching and caching the JWKS keys from Azure AD.
        Caching is enabled to improve performance and reduce the number of network requests to Azure AD.
        The cache will be refreshed after the specified TTL expires.
        """
        return jwt.PyJWKClient(
            self.discovery_keys_url,
            cache_jwk_set=True,
            cache_keys=True,
            lifespan=JWT_SET_CACHE_TTL_SECONDS,
        )

    @cached_property
    def discovery_keys_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"

    @property
    def audience(self) -> str | None:
        """
        The expected audience claim in the JWT token. This should match the API_AUDIENCE environment variable.
        """
        return os.getenv("API_AUDIENCE")

    @property
    def tenant_id(self) -> str | None:
        """
        The Azure AD tenant ID. This should be set as the TENANT_ID environment variable.
        """
        return os.getenv("TENANT_ID", "")

    @cached_property
    def issuers(self) -> list:
        """
        The expected issuer claim(s) in the JWT token. This should match the tenant ID and the Azure AD endpoints.
        """
        return [
            f"https://sts.windows.net/{self.tenant_id}/",
            f"https://login.microsoftonline.com/{self.tenant_id}/v2.0/",
        ]

    @property
    def bypass_authentication(self) -> bool:
        return getattr(settings, "BYPASS_API_AUTHENTICATION", False)
