import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sources.google_sheets_source import GoogleSheetsSource


@pytest.fixture
def sheets_config():
    return {
        'type': 'google_sheets',
        'spreadsheet_id': 'test-spreadsheet-id',
        'sheet_name': 'Pipeline',
        'content_columns': ['A', 'B', 'C'],
        'author_column': 'D',
        'timestamp_column': 'E',
        'lookback_hours': 168,
        '_google_config': {
            'credentials_path': '/tmp/test-creds.json',
            'client_id': 'test-id',
            'client_secret': 'test-secret',
            'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        }
    }


class TestGoogleSheetsSource:
    def test_is_available_no_spreadsheet_id(self, sample_persona):
        config = {'type': 'google_sheets', 'spreadsheet_id': ''}
        source = GoogleSheetsSource(config, sample_persona)
        assert source.is_available() is False

    def test_is_available_no_auth(self, sample_persona, sheets_config):
        source = GoogleSheetsSource(sheets_config, sample_persona)
        with patch.object(source, '_get_auth_manager') as mock_auth:
            mock_auth.return_value.is_authenticated.return_value = False
            assert source.is_available() is False

    def test_extract_returns_empty_when_unavailable(self, sample_persona):
        config = {'type': 'google_sheets', 'spreadsheet_id': ''}
        source = GoogleSheetsSource(config, sample_persona)
        assert source.extract() == []

    @patch('sources.google_sheets_source.GoogleSheetsSource._get_auth_manager')
    def test_extract_parses_rows(self, mock_auth_method, sample_persona, sheets_config):
        source = GoogleSheetsSource(sheets_config, sample_persona)

        # Mock the sheets API
        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_values = mock_service.spreadsheets.return_value.values.return_value
        mock_values.get.return_value.execute.return_value = {
            'values': [
                ['Title', 'Description', 'Status', 'Author', 'Date'],  # Headers
                ['Fix bug', 'Urgent fix needed', 'Open', 'Alice', '2026-02-20'],
                ['Add feature', 'New dashboard', 'In Progress', 'Bob', '2026-02-19'],
            ]
        }

        items = source.extract()
        assert len(items) == 2
        assert 'Fix bug' in items[0]['content']
        assert items[0]['metadata']['source_type'] == 'google_sheets'
        assert items[0]['metadata']['spreadsheet_id'] == 'test-spreadsheet-id'

    @patch('sources.google_sheets_source.GoogleSheetsSource._get_auth_manager')
    def test_extract_skips_empty_rows(self, mock_auth_method, sample_persona, sheets_config):
        source = GoogleSheetsSource(sheets_config, sample_persona)

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_values = mock_service.spreadsheets.return_value.values.return_value
        mock_values.get.return_value.execute.return_value = {
            'values': [
                ['Title', 'Description', 'Status', 'Author', 'Date'],
                ['', '', '', '', ''],  # Empty row
                ['Valid item', 'Has content', 'Open', 'Alice', '2026-02-20'],
            ]
        }

        items = source.extract()
        assert len(items) == 1
        assert 'Valid item' in items[0]['content']

    def test_parse_timestamp_various_formats(self, sample_persona, sheets_config):
        source = GoogleSheetsSource(sheets_config, sample_persona)

        assert source._parse_timestamp('2026-02-20 10:30:00') is not None
        assert source._parse_timestamp('2026-02-20') is not None
        assert source._parse_timestamp('02/20/2026') is not None
        assert source._parse_timestamp('invalid') is None
        assert source._parse_timestamp('') is None

    @patch('sources.google_sheets_source.GoogleSheetsSource._get_auth_manager')
    def test_extract_no_data(self, mock_auth_method, sample_persona, sheets_config):
        source = GoogleSheetsSource(sheets_config, sample_persona)

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_values = mock_service.spreadsheets.return_value.values.return_value
        mock_values.get.return_value.execute.return_value = {'values': []}

        items = source.extract()
        assert items == []
