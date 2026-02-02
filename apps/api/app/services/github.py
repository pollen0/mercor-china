"""
GitHub OAuth service for connecting student GitHub profiles.
"""
import httpx
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from ..config import settings

logger = logging.getLogger("pathway.github")


@dataclass
class GitHubUser:
    """GitHub user profile data."""
    id: int
    login: str  # username
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    public_repos: int
    followers: int
    following: int
    created_at: str


@dataclass
class GitHubRepo:
    """GitHub repository data."""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    language: Optional[str]
    stargazers_count: int
    forks_count: int
    updated_at: str
    topics: list[str]
    is_fork: bool = False
    owner_login: Optional[str] = None  # To show if user owns or collaborates


class GitHubService:
    """Service for GitHub OAuth and API interactions."""

    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_BASE_URL = "https://api.github.com"

    # Scopes we request
    SCOPES = ["read:user", "user:email", "repo"]

    def __init__(self):
        self.client_id = settings.github_client_id
        self.client_secret = settings.github_client_secret

    def is_configured(self) -> bool:
        """Check if GitHub OAuth is properly configured."""
        return bool(self.client_id and self.client_secret)

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate GitHub OAuth authorization URL.

        Args:
            redirect_uri: Where to redirect after authorization
            state: CSRF protection token

        Returns:
            Authorization URL to redirect user to
        """
        scope = " ".join(self.SCOPES)
        return (
            f"{self.AUTHORIZE_URL}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&state={state}"
        )

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub callback

        Returns:
            Access token for API calls
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.text}")
                raise Exception("Failed to exchange code for token")

            data = response.json()

            if "error" in data:
                error_code = data.get("error", "")
                error_desc = data.get("error_description", "")
                logger.error(f"GitHub OAuth error: {error_code} - {error_desc}")

                # Provide specific error messages for common OAuth errors
                if error_code == "bad_verification_code":
                    raise Exception(
                        "Authorization code has expired or already been used. "
                        "Please try connecting GitHub again."
                    )
                elif error_code == "incorrect_client_credentials":
                    raise Exception("GitHub OAuth configuration error. Please contact support.")
                elif error_code == "redirect_uri_mismatch":
                    raise Exception("OAuth redirect configuration error. Please contact support.")
                else:
                    raise Exception(error_desc or error_code)

            return data["access_token"]

    async def get_user(self, access_token: str) -> GitHubUser:
        """
        Get authenticated user's profile.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            GitHubUser with profile data
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.API_BASE_URL}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                logger.error(f"GitHub user fetch failed: {response.text}")
                raise Exception("Failed to fetch GitHub user")

            data = response.json()

            return GitHubUser(
                id=data["id"],
                login=data["login"],
                name=data.get("name"),
                email=data.get("email"),
                avatar_url=data.get("avatar_url"),
                bio=data.get("bio"),
                public_repos=data.get("public_repos", 0),
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                created_at=data.get("created_at", ""),
            )

    async def get_user_email(self, access_token: str) -> Optional[str]:
        """
        Get user's primary email (may not be public).

        Args:
            access_token: GitHub OAuth access token

        Returns:
            Primary email address or None
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.API_BASE_URL}/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )

            if response.status_code != 200:
                return None

            emails = response.json()

            # Find primary email
            for email in emails:
                if email.get("primary") and email.get("verified"):
                    return email["email"]

            # Fall back to any verified email
            for email in emails:
                if email.get("verified"):
                    return email["email"]

            return None

    async def get_repos(
        self, access_token: str, limit: int = 30, include_collaborator: bool = True
    ) -> list[GitHubRepo]:
        """
        Get user's repositories sorted by recently updated.

        Args:
            access_token: GitHub OAuth access token
            limit: Maximum number of repos to return
            include_collaborator: If True, includes repos the user collaborates on

        Returns:
            List of GitHubRepo objects
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use affiliation to get both owned and collaborated repos
            affiliation = "owner,collaborator" if include_collaborator else "owner"
            response = await client.get(
                f"{self.API_BASE_URL}/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                params={
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": limit,
                    "affiliation": affiliation,  # owner + collaborator repos
                },
            )

            if response.status_code != 200:
                logger.error(f"GitHub repos fetch failed: {response.text}")
                return []

            repos_data = response.json()

            return [
                GitHubRepo(
                    id=repo["id"],
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    html_url=repo["html_url"],
                    language=repo.get("language"),
                    stargazers_count=repo.get("stargazers_count", 0),
                    forks_count=repo.get("forks_count", 0),
                    updated_at=repo.get("updated_at", ""),
                    topics=repo.get("topics", []),
                    is_fork=repo.get("fork", False),
                    owner_login=repo.get("owner", {}).get("login"),
                )
                for repo in repos_data
            ]

    async def get_languages(self, access_token: str) -> dict[str, int]:
        """
        Aggregate languages across all user repos.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            Dict mapping language name to total bytes
        """
        repos = await self.get_repos(access_token, limit=20)
        languages: dict[str, int] = {}

        async with httpx.AsyncClient(timeout=30.0) as client:
            for repo in repos[:10]:  # Limit API calls
                response = await client.get(
                    f"{self.API_BASE_URL}/repos/{repo.full_name}/languages",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                    },
                )

                if response.status_code == 200:
                    repo_langs = response.json()
                    for lang, bytes_count in repo_langs.items():
                        languages[lang] = languages.get(lang, 0) + bytes_count

        return languages

    async def get_contribution_count(self, username: str) -> int:
        """
        Get approximate contribution count for a user.
        Note: This is a rough estimate from public events.

        Args:
            username: GitHub username

        Returns:
            Estimated contribution count
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.API_BASE_URL}/users/{username}/events/public",
                headers={"Accept": "application/vnd.github+json"},
                params={"per_page": 100},
            )

            if response.status_code != 200:
                return 0

            events = response.json()

            # Count push events and PR events
            contribution_events = ["PushEvent", "PullRequestEvent", "CreateEvent"]
            count = sum(
                1 for event in events if event.get("type") in contribution_events
            )

            return count

    async def get_full_profile(self, access_token: str) -> dict:
        """
        Get complete GitHub profile data for a user.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            Dict with user info, repos, languages, contributions
        """
        user = await self.get_user(access_token)
        email = await self.get_user_email(access_token)
        # Get repos including collaborator repos (repos user was invited to)
        repos = await self.get_repos(access_token, limit=30, include_collaborator=True)
        languages = await self.get_languages(access_token)
        contributions = await self.get_contribution_count(user.login)

        return {
            "username": user.login,
            "name": user.name,
            "email": email or user.email,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at,
            "top_repos": [
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "topics": repo.topics,
                    "updated_at": repo.updated_at,
                    "is_fork": repo.is_fork,
                    "owner": repo.owner_login,
                    "is_owner": repo.owner_login == user.login,
                }
                for repo in repos
            ],
            "languages": languages,
            "total_contributions": contributions,
        }


# Singleton instance
github_service = GitHubService()
