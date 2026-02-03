"""
GitHub App Authentication

Handles JWT generation and installation token retrieval for GitHub App API access.
"""

import os
import time
import jwt
import requests
from typing import Dict, Optional
from functools import lru_cache


class GitHubAppAuth:
    """Manages GitHub App authentication and installation tokens."""

    def __init__(self, app_id: str, private_key: str):
        """
        Initialize GitHub App authentication.

        Args:
            app_id: GitHub App ID
            private_key: Private key (PEM format) for signing JWTs
        """
        self.app_id = app_id
        self.private_key = private_key

    def generate_jwt(self, expiration: int = 600) -> str:
        """
        Generate a JWT for authenticating as the GitHub App.

        Args:
            expiration: Token expiration in seconds (max 600)

        Returns:
            JWT token string
        """
        now = int(time.time())
        payload = {
            "iat": now,  # Issued at time
            "exp": now + expiration,  # JWT expiration time
            "iss": self.app_id,  # GitHub App ID
        }

        # Encode and sign the JWT
        token = jwt.encode(payload, self.private_key, algorithm="RS256")
        return token

    @lru_cache(maxsize=128)
    def get_installation_token(self, installation_id: int) -> str:
        """
        Get an installation access token for accessing a specific installation.

        Installation tokens expire after 1 hour and are cached.

        Args:
            installation_id: Installation ID for the app on a specific account/org

        Returns:
            Installation access token

        Raises:
            Exception: If token generation fails
        """
        jwt_token = self.generate_jwt()

        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.post(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data["token"]

    def get_authenticated_headers(self, installation_id: int) -> Dict[str, str]:
        """
        Get headers with installation token for API requests.

        Args:
            installation_id: Installation ID

        Returns:
            Headers dict with Authorization
        """
        token = self.get_installation_token(installation_id)
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }


def create_auth_from_env() -> Optional[GitHubAppAuth]:
    """
    Create GitHubAppAuth from environment variables.

    Required env vars:
        GITHUB_APP_ID: App ID
        GITHUB_APP_PRIVATE_KEY: Private key (PEM format, use \\n for newlines)

    Returns:
        GitHubAppAuth instance or None if env vars not set
    """
    app_id = os.getenv("GITHUB_APP_ID")
    private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")

    if not app_id or not private_key:
        return None

    # Handle escaped newlines in env var
    private_key = private_key.replace("\\n", "\n")

    return GitHubAppAuth(app_id, private_key)
