from unittest.mock import Mock, patch

import jwt
import pytest
from django.conf import settings

from ..authentication import Authentication


@patch(f"{Authentication.__module__}.logger")
class TestAuthentication:
    @pytest.fixture(autouse=True)
    def setup_env(self):
        with patch.dict(
            "os.environ",
            {
                "API_AUDIENCE": "test_audience",
                "TENANT_ID": "test_tenant_id",
                "BYPASS_API_TOKEN_AUTH": "false",
            },
        ):
            yield

    @pytest.fixture
    def mock_jwks_signing_key(self):
        with patch.object(
            jwt.PyJWKClient,
            "get_signing_key_from_jwt",
            return_value=Mock(key="test_signing_key"),
        ):
            yield

    @patch.object(
        jwt.PyJWKClient, "get_signing_key_from_jwt", side_effect=jwt.PyJWKClientError
    )
    def test_with_no_matching_signing_key(self, mock_signing_key_error, mock_logger):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with(
            "Error fetching JWKS keys from Azure AD."
        )

    @patch(
        f"{Authentication.__module__}.jwt.decode", side_effect=jwt.ExpiredSignatureError
    )
    def test_with_expired_signature(
        self, mock_decode, mock_logger, mock_jwks_signing_key
    ):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with("Token is expired")

    @patch(
        f"{Authentication.__module__}.jwt.decode", side_effect=jwt.InvalidAudienceError
    )
    def test_with_invalid_claims(self, _, mock_logger, mock_jwks_signing_key):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with(
            "Invalid claims. Please check the audience and issuer."
        )

    @patch(
        f"{Authentication.__module__}.jwt.decode", side_effect=jwt.InvalidIssuerError
    )
    def test_with_invalid_issuer(self, _, mock_logger, mock_jwks_signing_key):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with(
            "Invalid claims. Please check the audience and issuer."
        )

    @patch(f"{Authentication.__module__}.jwt.decode", side_effect=jwt.InvalidTokenError)
    def test_with_invalid_token(self, _, mock_logger, mock_jwks_signing_key):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with("Token is invalid")

    @patch(f"{Authentication.__module__}.jwt.decode", side_effect=Exception)
    def test_with_unexpected_exception(self, _, mock_logger, mock_jwks_signing_key):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) is None
        mock_logger.exception.assert_called_with(
            "Unable to parse authentication token."
        )

    @patch(
        f"{Authentication.__module__}.jwt.decode", return_value={"sub": "1234567890"}
    )
    def test_with_valid_token(self, _, mock_logger, mock_jwks_signing_key):
        authenticator = Authentication()
        assert authenticator(Mock(headers={"Authorization": "Bearer abc123"})) == {
            "sub": "1234567890"
        }
        mock_logger.exception.assert_not_called()

    def test_request_auth_object_is_set(self, mock_logger, mock_jwks_signing_key):
        with patch(
            f"{Authentication.__module__}.jwt.decode",
            return_value={"oid": "test_oid", "sub": "test_user"},
        ):
            authenticator = Authentication()
            request = Mock(headers={"Authorization": "Bearer abc123"})
            assert authenticator(request) == {"oid": "test_oid", "sub": "test_user"}
            assert request.auth == {"oid": "test_oid", "sub": "test_user"}

    def test_authentication_bypass_enabled(self, mock_logger, mock_jwks_signing_key):
        with patch.object(settings, "BYPASS_API_AUTHENTICATION", return_value=True):
            authenticator = Authentication()
            assert authenticator(
                Mock(headers={"Authorization": "Bearer anytoken"})
            ) == {"oid": "bypass_object_id", "sub": "bypass_user"}
