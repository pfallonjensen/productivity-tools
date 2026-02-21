import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from engine.google_auth import GoogleAuthManager


@pytest.fixture
def google_config(tmp_path):
    return {
        'credentials_path': str(tmp_path / 'google-credentials.json'),
        'client_id': 'test-client-id.apps.googleusercontent.com',
        'client_secret': 'test-client-secret',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/spreadsheets.readonly',
        ],
    }


@pytest.fixture
def stored_token_data():
    return {
        'access_token': 'ya29.test-access-token',
        'refresh_token': '1//test-refresh-token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'test-client-id.apps.googleusercontent.com',
        'client_secret': 'test-client-secret',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/spreadsheets.readonly',
        ],
    }


@pytest.fixture
def auth_manager(google_config):
    return GoogleAuthManager(google_config)


class TestGoogleAuthManager:
    def test_init_expands_tilde(self):
        """credentials_path with ~ expands to home directory"""
        config = {
            'credentials_path': '~/.config/test/creds.json',
            'client_id': 'cid',
            'client_secret': 'csec',
            'scopes': [],
        }
        mgr = GoogleAuthManager(config)
        assert '~' not in str(mgr.credentials_path)
        assert str(mgr.credentials_path).startswith('/')

    def test_init_stores_config(self, auth_manager, google_config):
        """GoogleAuthManager stores config values from google section"""
        assert auth_manager.client_id == google_config['client_id']
        assert auth_manager.client_secret == google_config['client_secret']
        assert auth_manager.scopes == google_config['scopes']

    def test_load_stored_credentials_file_missing(self, auth_manager):
        """Returns None when credentials file doesn't exist"""
        result = auth_manager._load_stored_credentials()
        assert result is None

    def test_load_stored_credentials_valid_file(self, auth_manager, stored_token_data):
        """Loads credentials from existing JSON token file"""
        auth_manager.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        auth_manager.credentials_path.write_text(json.dumps(stored_token_data))

        creds = auth_manager._load_stored_credentials()
        assert creds is not None
        assert creds.token == 'ya29.test-access-token'
        assert creds.refresh_token == '1//test-refresh-token'
        assert creds.client_id == stored_token_data['client_id']

    def test_load_stored_credentials_malformed_json(self, auth_manager):
        """Returns None for malformed JSON"""
        auth_manager.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        auth_manager.credentials_path.write_text('not valid json{{{')

        result = auth_manager._load_stored_credentials()
        assert result is None

    def test_load_stored_credentials_no_refresh_token(self, auth_manager, stored_token_data):
        """Loads credentials even if refresh_token is absent"""
        stored_token_data.pop('refresh_token')
        auth_manager.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        auth_manager.credentials_path.write_text(json.dumps(stored_token_data))

        creds = auth_manager._load_stored_credentials()
        assert creds is not None
        assert creds.refresh_token is None

    def test_save_credentials_creates_parent_dirs(self, auth_manager):
        """_save_credentials creates parent directories if missing"""
        nested_path = auth_manager.credentials_path.parent / 'deep' / 'nested'
        auth_manager.credentials_path = nested_path / 'creds.json'

        mock_creds = MagicMock()
        mock_creds.token = 'access'
        mock_creds.refresh_token = 'refresh'
        mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
        mock_creds.client_id = 'cid'
        mock_creds.client_secret = 'csec'
        mock_creds.scopes = ['scope1']

        auth_manager._save_credentials(mock_creds)

        assert auth_manager.credentials_path.exists()
        saved = json.loads(auth_manager.credentials_path.read_text())
        assert saved['access_token'] == 'access'
        assert saved['refresh_token'] == 'refresh'

    @patch('engine.google_auth.Credentials')
    def test_get_credentials_returns_cached(self, mock_creds_cls, auth_manager):
        """Returns cached credentials if still valid"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        auth_manager._credentials = mock_creds

        result = auth_manager.get_credentials()
        assert result is mock_creds

    @patch('engine.google_auth.Request')
    def test_get_credentials_refreshes_expired(self, mock_request_cls, auth_manager, stored_token_data):
        """Refreshes expired credentials that have a refresh token"""
        auth_manager.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        auth_manager.credentials_path.write_text(json.dumps(stored_token_data))

        with patch('engine.google_auth.Credentials') as mock_creds_cls:
            mock_creds = MagicMock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = '1//test-refresh-token'
            mock_creds.token = 'new-access-token'
            mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
            mock_creds.client_id = 'cid'
            mock_creds.client_secret = 'csec'
            mock_creds.scopes = ['scope1']

            # After refresh, mark as valid
            def mark_valid(request):
                mock_creds.valid = True
            mock_creds.refresh.side_effect = mark_valid

            mock_creds_cls.return_value = mock_creds
            auth_manager._credentials = None

            result = auth_manager.get_credentials()
            mock_creds.refresh.assert_called_once()
            assert result.valid is True

    @patch('engine.google_auth.InstalledAppFlow')
    def test_get_credentials_runs_oauth_flow(self, mock_flow_cls, auth_manager):
        """Falls back to OAuth flow when no stored credentials exist"""
        mock_flow = MagicMock()
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = 'new-token'
        mock_creds.refresh_token = 'new-refresh'
        mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
        mock_creds.client_id = 'cid'
        mock_creds.client_secret = 'csec'
        mock_creds.scopes = ['scope1']

        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_cls.from_client_config.return_value = mock_flow

        result = auth_manager.get_credentials()
        mock_flow_cls.from_client_config.assert_called_once()
        mock_flow.run_local_server.assert_called_once_with(port=0)
        assert result is mock_creds

    @patch('engine.google_auth.build')
    def test_get_service_builds_correct_service(self, mock_build, auth_manager):
        """get_service calls googleapiclient.discovery.build with correct args"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        auth_manager._credentials = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        result = auth_manager.get_service('gmail', 'v1')
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        assert result is mock_service

    @patch('engine.google_auth.build')
    def test_get_service_sheets(self, mock_build, auth_manager):
        """get_service works for Sheets API"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        auth_manager._credentials = mock_creds

        auth_manager.get_service('sheets', 'v4')
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

    def test_is_authenticated_no_credentials(self, auth_manager):
        """is_authenticated returns False when no credentials exist"""
        assert auth_manager.is_authenticated() is False

    def test_is_authenticated_with_valid_cached(self, auth_manager):
        """is_authenticated returns True with valid cached credentials"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        auth_manager._credentials = mock_creds
        assert auth_manager.is_authenticated() is True

    def test_is_authenticated_loads_from_file(self, auth_manager, stored_token_data):
        """is_authenticated loads and checks stored credentials"""
        auth_manager.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        auth_manager.credentials_path.write_text(json.dumps(stored_token_data))

        with patch.object(auth_manager, '_load_stored_credentials') as mock_load:
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_load.return_value = mock_creds

            assert auth_manager.is_authenticated() is True

    @patch('engine.google_auth.Request')
    def test_is_authenticated_refreshes_expired(self, mock_request_cls, auth_manager):
        """is_authenticated refreshes expired creds without triggering OAuth flow"""
        with patch.object(auth_manager, '_load_stored_credentials') as mock_load:
            mock_creds = MagicMock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = 'refresh-token'
            mock_load.return_value = mock_creds

            with patch.object(auth_manager, '_refresh_credentials') as mock_refresh:
                refreshed = MagicMock()
                refreshed.valid = True
                mock_refresh.return_value = refreshed

                with patch.object(auth_manager, '_save_credentials'):
                    assert auth_manager.is_authenticated() is True

    def test_is_authenticated_expired_no_refresh_token(self, auth_manager):
        """is_authenticated returns False when expired with no refresh token"""
        with patch.object(auth_manager, '_load_stored_credentials') as mock_load:
            mock_creds = MagicMock()
            mock_creds.valid = False
            mock_creds.expired = True
            mock_creds.refresh_token = None
            mock_load.return_value = mock_creds

            assert auth_manager.is_authenticated() is False

    @patch('engine.google_auth.Request')
    def test_refresh_credentials_failure(self, mock_request_cls, auth_manager):
        """_refresh_credentials returns None on failure"""
        mock_creds = MagicMock()
        mock_creds.refresh.side_effect = Exception("Network error")

        result = auth_manager._refresh_credentials(mock_creds)
        assert result is None
