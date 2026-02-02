"""
Google Calendar integration service.
Handles OAuth, calendar access, and Google Meet invite generation.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx

from ..config import settings
from ..utils.crypto import encrypt_token, decrypt_token

logger = logging.getLogger("pathway.calendar")

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"

# OAuth scopes needed
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",  # Create/modify events
    "https://www.googleapis.com/auth/calendar.readonly",  # Read calendar
]


class GoogleCalendarService:
    """Service for Google Calendar integration."""

    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri

    def is_configured(self) -> bool:
        """Check if Google Calendar OAuth is configured."""
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    def get_oauth_url(self, state: str) -> str:
        """
        Generate Google OAuth URL for calendar authorization.

        Args:
            state: CSRF state token (should be stored in session/cookie)

        Returns:
            OAuth authorization URL
        """
        if not self.is_configured():
            raise ValueError("Google Calendar OAuth is not configured")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",  # Get refresh token
            "prompt": "consent",  # Force consent to get refresh token
            "state": state,
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dict with access_token, refresh_token, expires_in
        """
        if not self.is_configured():
            raise ValueError("Google Calendar OAuth is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )

            if response.status_code != 200:
                logger.error(f"Google token exchange failed: {response.text}")
                raise ValueError(f"Failed to exchange code: {response.text}")

            data = response.json()
            return {
                "access_token": encrypt_token(data["access_token"]),
                "refresh_token": encrypt_token(data.get("refresh_token", "")),
                "expires_in": data.get("expires_in", 3600),
            }

    async def refresh_access_token(self, encrypted_refresh_token: str) -> dict:
        """
        Refresh the access token using refresh token.

        Args:
            encrypted_refresh_token: Encrypted refresh token

        Returns:
            Dict with new access_token, expires_in
        """
        if not self.is_configured():
            raise ValueError("Google Calendar OAuth is not configured")

        refresh_token = decrypt_token(encrypted_refresh_token)
        if not refresh_token:
            raise ValueError("Invalid refresh token")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                logger.error(f"Google token refresh failed: {response.text}")
                raise ValueError("Failed to refresh token")

            data = response.json()
            return {
                "access_token": encrypt_token(data["access_token"]),
                "expires_in": data.get("expires_in", 3600),
            }

    async def create_meeting_event(
        self,
        encrypted_access_token: str,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendee_emails: list[str],
        timezone: str = "America/Los_Angeles",
    ) -> dict:
        """
        Create a calendar event with Google Meet link.

        Args:
            encrypted_access_token: Encrypted access token
            title: Event title
            description: Event description
            start_time: Event start time
            end_time: Event end time
            attendee_emails: List of attendee email addresses
            timezone: Timezone for the event

        Returns:
            Dict with event_id, html_link, hangout_link (Google Meet URL)
        """
        access_token = decrypt_token(encrypted_access_token)
        if not access_token:
            raise ValueError("Invalid access token")

        # Build event data with Google Meet conferencing
        event_data = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
            "attendees": [{"email": email} for email in attendee_emails],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"pathway-{start_time.timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 day before
                    {"method": "popup", "minutes": 30},  # 30 min before
                ],
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
                params={"conferenceDataVersion": 1, "sendUpdates": "all"},
                headers={"Authorization": f"Bearer {access_token}"},
                json=event_data,
            )

            if response.status_code not in (200, 201):
                logger.error(f"Failed to create calendar event: {response.text}")
                raise ValueError(f"Failed to create event: {response.text}")

            event = response.json()

            # Extract Google Meet link
            meet_link = None
            if "conferenceData" in event:
                entry_points = event["conferenceData"].get("entryPoints", [])
                for ep in entry_points:
                    if ep.get("entryPointType") == "video":
                        meet_link = ep.get("uri")
                        break

            return {
                "event_id": event["id"],
                "html_link": event.get("htmlLink"),
                "hangout_link": meet_link,
            }

    async def cancel_event(
        self,
        encrypted_access_token: str,
        event_id: str,
        send_updates: bool = True,
    ) -> bool:
        """
        Cancel/delete a calendar event.

        Args:
            encrypted_access_token: Encrypted access token
            event_id: Google Calendar event ID
            send_updates: Whether to notify attendees

        Returns:
            True if successful
        """
        access_token = decrypt_token(encrypted_access_token)
        if not access_token:
            raise ValueError("Invalid access token")

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{GOOGLE_CALENDAR_API}/calendars/primary/events/{event_id}",
                params={"sendUpdates": "all" if send_updates else "none"},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 204):
                logger.error(f"Failed to cancel event: {response.text}")
                return False

            return True

    async def get_free_busy(
        self,
        encrypted_access_token: str,
        time_min: datetime,
        time_max: datetime,
        timezone: str = "America/Los_Angeles",
    ) -> list[dict]:
        """
        Get busy times from calendar for scheduling.

        Args:
            encrypted_access_token: Encrypted access token
            time_min: Start of time range
            time_max: End of time range
            timezone: Timezone

        Returns:
            List of busy time periods [{start, end}]
        """
        access_token = decrypt_token(encrypted_access_token)
        if not access_token:
            raise ValueError("Invalid access token")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GOOGLE_CALENDAR_API}/freeBusy",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "timeMin": time_min.isoformat(),
                    "timeMax": time_max.isoformat(),
                    "timeZone": timezone,
                    "items": [{"id": "primary"}],
                },
            )

            if response.status_code != 200:
                logger.error(f"Failed to get free/busy: {response.text}")
                return []

            data = response.json()
            calendars = data.get("calendars", {})
            primary = calendars.get("primary", {})
            return primary.get("busy", [])


# Singleton instance
calendar_service = GoogleCalendarService()
