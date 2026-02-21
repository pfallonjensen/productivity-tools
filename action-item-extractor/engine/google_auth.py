"""
Google OAuth manager — shared authentication for Google API sources.
Handles OAuth 2.0 flow, token storage, and credential refresh.
"""
import json
import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleAuthManager:
    """Manages Google OAuth 2.0 credentials for API access."""

    def __init__(self, google_config: dict):
        self.logger = logging.getLogger('GoogleAuthManager')
        self.credentials_path = Path(
            google_config.get('credentials_path', '')
        ).expanduser()
        self.client_id = google_config.get('client_id', '')
        self.client_secret = google_config.get('client_secret', '')
        self.scopes = google_config.get('scopes', [])
        self._credentials: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing or running OAuth flow as needed."""
        if self._credentials and self._credentials.valid:
            return self._credentials

        # Try loading stored credentials
        creds = self._load_stored_credentials()

        if creds and creds.valid:
            self.logger.info("Using valid stored credentials")
            self._credentials = creds
            return self._credentials

        if creds and creds.expired and creds.refresh_token:
            self.logger.info("Stored credentials expired, refreshing")
            creds = self._refresh_credentials(creds)
            if creds and creds.valid:
                self._save_credentials(creds)
                self._credentials = creds
                return self._credentials

        # No valid credentials — run interactive OAuth flow
        self.logger.info("No valid credentials found, starting OAuth flow")
        creds = self._run_oauth_flow()
        self._save_credentials(creds)
        self._credentials = creds
        return self._credentials

    def get_service(self, service_name: str, version: str):
        """Build an authenticated Google API service."""
        creds = self.get_credentials()
        self.logger.info("Building service: %s %s", service_name, version)
        return build(service_name, version, credentials=creds)

    def is_authenticated(self) -> bool:
        """Check if valid credentials are available without triggering OAuth flow."""
        if self._credentials and self._credentials.valid:
            return True

        creds = self._load_stored_credentials()
        if creds and creds.valid:
            self._credentials = creds
            return True

        if creds and creds.expired and creds.refresh_token:
            refreshed = self._refresh_credentials(creds)
            if refreshed and refreshed.valid:
                self._save_credentials(refreshed)
                self._credentials = refreshed
                return True

        return False

    def _load_stored_credentials(self) -> Optional[Credentials]:
        """Load credentials from stored token file."""
        if not self.credentials_path.exists():
            self.logger.debug("No credentials file at %s", self.credentials_path)
            return None

        try:
            with open(self.credentials_path) as f:
                data = json.load(f)

            creds = Credentials(
                token=data.get('access_token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=data.get('client_id', self.client_id),
                client_secret=data.get('client_secret', self.client_secret),
                scopes=data.get('scopes', self.scopes),
            )
            self.logger.debug("Loaded credentials from %s", self.credentials_path)
            return creds
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning("Failed to load credentials: %s", e)
            return None

    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to token file."""
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes) if creds.scopes else self.scopes,
        }

        with open(self.credentials_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info("Saved credentials to %s", self.credentials_path)

    def _run_oauth_flow(self) -> Credentials:
        """Run interactive browser-based OAuth flow."""
        self.logger.info("Starting browser-based OAuth flow")

        client_config = {
            'installed': {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': ['http://localhost'],
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
        creds = flow.run_local_server(port=0)

        self.logger.info("OAuth flow completed successfully")
        return creds

    def _refresh_credentials(self, creds: Credentials) -> Optional[Credentials]:
        """Refresh expired credentials using refresh token."""
        try:
            creds.refresh(Request())
            self.logger.info("Credentials refreshed successfully")
            return creds
        except Exception as e:
            self.logger.warning("Failed to refresh credentials: %s", e)
            return None
