# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# Add the 'scripts' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from utils.github_app_auth import get_github_app_token, get_session


class TestGitHubAppAuth(unittest.TestCase):
    @patch("utils.github_app_auth.requests.Session")
    def test_get_session(self, mock_session):
        session = get_session()
        self.assertIsNotNone(session)
        mock_session.return_value.mount.assert_called_once()

    @patch("utils.github_app_auth.jwt.encode")
    @patch("utils.github_app_auth.get_session")
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data=b"test_pem_data")
    def test_get_github_app_token_success(self, mock_open, mock_get_session, mock_jwt_encode):
        # Mock the session and its responses
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Mock the response for installations
        mock_installations_response = MagicMock()
        mock_installations_response.status_code = 200
        mock_installations_response.json.return_value = [
            {"id": 123, "account": {"login": "SomeOtherOwner"}},
            {"id": 456, "account": {"login": "TestOwner"}},
        ]
        mock_installations_response.raise_for_status = MagicMock()

        # Mock the response for access token
        mock_token_response = MagicMock()
        mock_token_response.status_code = 201
        mock_token_response.json.return_value = {"token": "test_token"}
        mock_token_response.raise_for_status = MagicMock()

        mock_session.get.return_value = mock_installations_response
        mock_session.post.return_value = mock_token_response

        # Mock JWT encoding
        mock_jwt_encode.return_value = "test_jwt"

        token = get_github_app_token("test_client_id", "dummy/path/to.pem", "TestOwner")

        self.assertEqual(token, "test_token")
        mock_open.assert_called_once_with("dummy/path/to.pem", "rb")
        mock_get_session.assert_called_once()
        mock_jwt_encode.assert_called_once()
        mock_session.get.assert_called_with(
            "https://api.github.com/app/installations",
            headers={"Authorization": "Bearer test_jwt", "Accept": "application/vnd.github.v3+json"},
            timeout=30,
        )
        mock_session.post.assert_called_with(
            "https://api.github.com/app/installations/456/access_tokens",
            headers={"Authorization": "Bearer test_jwt", "Accept": "application/vnd.github.v3+json"},
            timeout=30,
        )

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_github_app_token_pem_not_found(self, mock_open):
        token = get_github_app_token("test_client_id", "nonexistent/path.pem", "TestOwner")
        self.assertIsNone(token)

    @patch("utils.github_app_auth.jwt.encode")
    @patch("utils.github_app_auth.get_session")
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data=b"test_pem_data")
    def test_get_github_app_token_installations_request_fails(self, mock_open, mock_get_session, mock_jwt_encode):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.get.side_effect = requests.exceptions.RequestException("API is down")
        mock_jwt_encode.return_value = "test_jwt"

        token = get_github_app_token("test_client_id", "dummy/path/to.pem", "TestOwner")
        self.assertIsNone(token)


if __name__ == "__main__":
    unittest.main()
