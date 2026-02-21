import pytest
from unittest.mock import patch, MagicMock
from sources.slack_source import SlackSource


@pytest.fixture
def slack_config():
    return {
        'type': 'slack',
        'token': 'xoxp-test-token',
        'workspace': 'test-workspace',
        'lookback_hours': 24,
        'user_id': 'U12345TEST'
    }


@pytest.fixture
def slack_source(slack_config, sample_persona):
    return SlackSource(slack_config, sample_persona)


class TestSlackSource:
    def test_is_available_with_token(self, slack_source):
        assert slack_source.is_available() is True

    def test_is_not_available_without_token(self, sample_persona):
        config = {'type': 'slack', 'token': '', 'workspace': 'test', 'lookback_hours': 24}
        source = SlackSource(config, sample_persona)
        assert source.is_available() is False

    @patch('sources.slack_source.requests.get')
    def test_extracts_dm_messages(self, mock_get, slack_source):
        # Mock conversations.list (DMs)
        dm_list_response = MagicMock()
        dm_list_response.json.return_value = {
            'ok': True,
            'channels': [{'id': 'D123', 'name': 'dm-channel'}]
        }

        # Mock conversations.history
        history_response = MagicMock()
        history_response.json.return_value = {
            'ok': True,
            'messages': [
                {
                    'text': 'Can you review the spec?',
                    'user': 'U999OTHER',
                    'ts': '1708300000.000000',
                    'type': 'message'
                }
            ]
        }

        # Mock users.info
        user_info_response = MagicMock()
        user_info_response.json.return_value = {
            'ok': True,
            'user': {'real_name': 'Boss Person', 'name': 'boss'}
        }

        mock_get.side_effect = [dm_list_response, history_response, user_info_response]

        items = slack_source._extract_dms(0)
        assert len(items) == 1
        assert 'review the spec' in items[0]['content']
        assert items[0]['author'] == 'Boss Person'

    @patch('sources.slack_source.requests.get')
    def test_skips_self_messages(self, mock_get, slack_source):
        dm_list_response = MagicMock()
        dm_list_response.json.return_value = {
            'ok': True,
            'channels': [{'id': 'D123', 'name': 'dm-channel'}]
        }

        history_response = MagicMock()
        history_response.json.return_value = {
            'ok': True,
            'messages': [
                {
                    'text': 'My own message',
                    'user': 'U12345TEST',
                    'ts': '1708300000.000000'
                }
            ]
        }

        mock_get.side_effect = [dm_list_response, history_response]

        items = slack_source._extract_dms(0)
        assert len(items) == 0

    @patch('sources.slack_source.requests.get')
    def test_builds_correct_slack_url(self, mock_get, slack_source):
        dm_list_response = MagicMock()
        dm_list_response.json.return_value = {
            'ok': True,
            'channels': [{'id': 'D123', 'name': 'dm-channel'}]
        }

        history_response = MagicMock()
        history_response.json.return_value = {
            'ok': True,
            'messages': [
                {
                    'text': 'Test message',
                    'user': 'U999',
                    'ts': '1708300000.123456'
                }
            ]
        }

        user_info_response = MagicMock()
        user_info_response.json.return_value = {
            'ok': True,
            'user': {'real_name': 'Someone', 'name': 'someone'}
        }

        mock_get.side_effect = [dm_list_response, history_response, user_info_response]

        items = slack_source._extract_dms(0)
        assert 'test-workspace.slack.com' in items[0]['url']
        assert 'D123' in items[0]['url']

    @patch('sources.slack_source.requests.get')
    def test_handles_api_error(self, mock_get, slack_source):
        error_response = MagicMock()
        error_response.json.return_value = {'ok': False, 'error': 'invalid_auth'}
        mock_get.return_value = error_response

        items = slack_source._extract_dms(0)
        assert len(items) == 0
