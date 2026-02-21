import pytest
import base64
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from email.utils import format_datetime
from sources.email_source import EmailSource


def _recent_email_date(hours_ago=1):
    """Generate an RFC 2822 date string relative to now (always within lookback)."""
    dt = datetime.now() - timedelta(hours=hours_ago)
    # format_datetime needs timezone-aware; use UTC offset for simplicity
    from datetime import timezone
    dt_utc = dt.astimezone(timezone.utc)
    return format_datetime(dt_utc)


@pytest.fixture
def gmail_config():
    return {
        'type': 'email',
        'provider': 'gmail',
        'labels': ['INBOX'],
        'lookback_hours': 24,
        'max_results': 100,
        '_google_config': {
            'credentials_path': '/tmp/test-creds.json',
            'client_id': 'test-id',
            'client_secret': 'test-secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly'],
        }
    }


class TestEmailSource:
    def test_is_available_no_provider(self, sample_persona):
        config = {'type': 'email', 'provider': 'imap'}
        source = EmailSource(config, sample_persona)
        assert source.is_available() is False

    def test_is_available_no_auth(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        with patch.object(source, '_get_auth_manager') as mock_auth:
            mock_auth.return_value.is_authenticated.return_value = False
            assert source.is_available() is False

    def test_extract_returns_empty_when_unavailable(self, sample_persona):
        config = {'type': 'email', 'provider': 'gmail', 'lookback_hours': 24}
        source = EmailSource(config, sample_persona)
        items = source.extract()
        assert items == []

    def test_extract_unsupported_provider(self, sample_persona):
        config = {'type': 'email', 'provider': 'imap', 'lookback_hours': 24,
                  '_google_config': {'credentials_path': '/tmp/x'}}
        source = EmailSource(config, sample_persona)
        items = source.extract()
        assert items == []

    @patch('sources.email_source.EmailSource._get_auth_manager')
    def test_extract_parses_gmail_messages(self, mock_auth_method, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        # Mock messages.list
        mock_users = mock_service.users.return_value
        mock_messages = mock_users.messages.return_value
        mock_messages.list.return_value.execute.return_value = {
            'messages': [{'id': 'msg1'}, {'id': 'msg2'}]
        }

        # Mock messages.get for each message (use relative dates to stay within lookback)
        body_text = base64.urlsafe_b64encode(b'Please review the deployment plan.').decode()
        mock_messages.get.return_value.execute.side_effect = [
            {
                'id': 'msg1',
                'threadId': 'thread1',
                'payload': {
                    'mimeType': 'text/plain',
                    'headers': [
                        {'name': 'Subject', 'value': 'Deployment Review Needed'},
                        {'name': 'From', 'value': 'Alice Smith <alice@example.com>'},
                        {'name': 'Date', 'value': _recent_email_date(hours_ago=2)},
                    ],
                    'body': {'data': body_text},
                }
            },
            {
                'id': 'msg2',
                'threadId': 'thread2',
                'payload': {
                    'mimeType': 'text/plain',
                    'headers': [
                        {'name': 'Subject', 'value': 'Quick Question'},
                        {'name': 'From', 'value': 'Bob <bob@example.com>'},
                        {'name': 'Date', 'value': _recent_email_date(hours_ago=3)},
                    ],
                    'body': {'data': base64.urlsafe_b64encode(b'Can you approve?').decode()},
                }
            },
        ]

        items = source.extract()
        assert len(items) == 2
        assert 'Deployment Review Needed' in items[0]['content']
        assert items[0]['author'] == 'Alice Smith'
        assert items[0]['metadata']['source_type'] == 'email'
        assert items[0]['metadata']['provider'] == 'gmail'
        assert items[0]['metadata']['thread_id'] == 'thread1'

    @patch('sources.email_source.EmailSource._get_auth_manager')
    def test_extract_no_messages(self, mock_auth_method, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            'messages': []
        }

        items = source.extract()
        assert items == []

    def test_extract_body_plain_text(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        body_text = base64.urlsafe_b64encode(b'Hello world').decode()
        payload = {
            'mimeType': 'text/plain',
            'body': {'data': body_text},
        }
        result = source._extract_body(payload)
        assert result == 'Hello world'

    def test_extract_body_multipart(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        body_text = base64.urlsafe_b64encode(b'Plain text part').decode()
        payload = {
            'mimeType': 'multipart/alternative',
            'parts': [
                {'mimeType': 'text/html', 'body': {'data': base64.urlsafe_b64encode(b'<p>html</p>').decode()}},
                {'mimeType': 'text/plain', 'body': {'data': body_text}},
            ]
        }
        result = source._extract_body(payload)
        assert result == 'Plain text part'

    def test_extract_body_empty(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        payload = {'mimeType': 'multipart/mixed', 'parts': []}
        result = source._extract_body(payload)
        assert result == ''

    def test_parse_email_date(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        dt = source._parse_email_date('Thu, 20 Feb 2026 10:30:00 +0000')
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 20

    def test_parse_email_date_empty(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        assert source._parse_email_date('') is None
        assert source._parse_email_date(None) is None

    def test_sender_name_extraction(self, sample_persona, gmail_config):
        source = EmailSource(gmail_config, sample_persona)
        msg = {
            'id': 'test',
            'threadId': 'thread',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': '"Fallon Jensen" <fallon@example.com>'},
                    {'name': 'Subject', 'value': 'Test'},
                    {'name': 'Date', 'value': _recent_email_date(hours_ago=1)},
                ],
                'mimeType': 'text/plain',
                'body': {'data': base64.urlsafe_b64encode(b'test').decode()},
            }
        }
        item = source._message_to_item(msg)
        assert item is not None
        assert item['author'] == 'Fallon Jensen'
