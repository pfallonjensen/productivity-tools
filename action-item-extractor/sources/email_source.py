"""
Email source plugin — scans Gmail for recent emails via Gmail API.
Uses GoogleAuthManager for authentication.
Falls back to placeholder behavior if Google auth is not configured.
"""
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sources.base_source import BaseSource


class EmailSource(BaseSource):
    """Scan Gmail for action items using the Gmail API."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.provider = source_config.get('provider', 'gmail')
        self.credentials_path = source_config.get('credentials_path', '')
        self.lookback_hours = source_config.get('lookback_hours', 24)
        self.labels = source_config.get('labels', ['INBOX'])
        self.max_results = source_config.get('max_results', 100)
        self._auth_manager = None
        self._google_config = source_config.get('_google_config', {})

    def _get_auth_manager(self):
        """Lazy-init GoogleAuthManager."""
        if self._auth_manager is None:
            from engine.google_auth import GoogleAuthManager
            self._auth_manager = GoogleAuthManager(self._google_config)
        return self._auth_manager

    def extract(self) -> List[Dict]:
        """Extract recent emails from Gmail as action item candidates."""
        if not self.is_available():
            self.logger.info("Email source not available — skipping")
            return []

        if self.provider != 'gmail':
            self.logger.info(f"Email provider '{self.provider}' not supported yet")
            return []

        try:
            service = self._get_auth_manager().get_service('gmail', 'v1')
            return self._fetch_gmail_messages(service)
        except Exception as e:
            self.logger.error(f"Error fetching Gmail messages: {e}")
            return []

    def _fetch_gmail_messages(self, service) -> List[Dict]:
        """Fetch messages from Gmail API."""
        # Build query: recent messages in specified labels
        after_date = datetime.now() - timedelta(hours=self.lookback_hours)
        after_str = after_date.strftime('%Y/%m/%d')
        query = f"after:{after_str}"

        # Add label filter
        label_ids = [label.upper() for label in self.labels]

        results = service.users().messages().list(
            userId='me',
            q=query,
            labelIds=label_ids,
            maxResults=self.max_results,
        ).execute()

        message_ids = results.get('messages', [])
        if not message_ids:
            self.logger.info("No Gmail messages found in lookback period")
            return []

        items = []
        for msg_ref in message_ids:
            msg = service.users().messages().get(
                userId='me',
                id=msg_ref['id'],
                format='full',
            ).execute()

            item = self._message_to_item(msg)
            if item:
                items.append(item)

        self.logger.info(f"Extracted {len(items)} items from Gmail")
        return items

    def _message_to_item(self, msg: dict) -> Optional[Dict]:
        """Convert a Gmail API message to a RawItem dict."""
        headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}

        subject = headers.get('subject', '(No Subject)')
        sender = headers.get('from', 'Unknown')
        date_str = headers.get('date', '')
        thread_id = msg.get('threadId', '')
        msg_id = msg.get('id', '')

        # Parse timestamp
        timestamp = self._parse_email_date(date_str)
        if timestamp and not self.is_within_lookback(timestamp, self.lookback_hours):
            return None

        # Extract body text
        body = self._extract_body(msg.get('payload', {}))

        # Combine subject + body for content
        content = f"Subject: {subject}\n\n{body}" if body else f"Subject: {subject}"

        # Extract sender name (strip email address)
        sender_name = sender.split('<')[0].strip().strip('"')
        if not sender_name:
            sender_name = sender

        return {
            'content': content,
            'author': sender_name,
            'timestamp': timestamp or datetime.now(),
            'url': f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
            'metadata': {
                'source_type': 'email',
                'provider': 'gmail',
                'subject': subject,
                'thread_id': thread_id,
                'message_id': msg_id,
                'sender_full': sender,
            }
        }

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from Gmail message payload."""
        # Direct body (simple messages)
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        # Multipart messages — look for text/plain part
        parts = payload.get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

            # Nested multipart
            if part.get('parts'):
                for subpart in part['parts']:
                    if subpart.get('mimeType') == 'text/plain':
                        data = subpart.get('body', {}).get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        return ''

    @staticmethod
    def _parse_email_date(date_str: str) -> Optional[datetime]:
        """Parse email Date header into datetime."""
        if not date_str:
            return None

        from email.utils import parsedate_to_datetime
        try:
            dt = parsedate_to_datetime(date_str)
            return dt.replace(tzinfo=None)
        except Exception:
            return None

    def is_available(self) -> bool:
        """Check if email source is configured and authenticated."""
        if self.provider != 'gmail':
            return False
        try:
            return self._get_auth_manager().is_authenticated()
        except Exception:
            # Fall back to legacy check for backward compatibility
            if self.credentials_path:
                from pathlib import Path
                return Path(self.credentials_path).exists()
            return False
