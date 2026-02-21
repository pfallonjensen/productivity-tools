import pytest
from unittest.mock import patch, MagicMock
from sources.jira_source import JiraSource


@pytest.fixture
def jira_config():
    return {
        'type': 'jira',
        'cloud_id': 'test-cloud-id',
        'token': 'test-jira-token',
        'email': 'test@example.com',
        'lookback_days': 7,
        'projects': ['PROJ']
    }


class TestJiraSource:
    def test_is_available_with_config(self, jira_config, sample_persona):
        source = JiraSource(jira_config, sample_persona)
        assert source.is_available() is True

    def test_is_not_available_without_token(self, sample_persona):
        config = {'type': 'jira', 'cloud_id': '', 'token': '', 'email': '', 'lookback_days': 7}
        source = JiraSource(config, sample_persona)
        assert source.is_available() is False

    @patch('sources.jira_source.requests.get')
    def test_extracts_assigned_issues(self, mock_get, jira_config, sample_persona):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'issues': [{
                'key': 'PROJ-123',
                'fields': {
                    'summary': 'Fix the login bug',
                    'assignee': {'displayName': 'Test User'},
                    'reporter': {'displayName': 'Boss'},
                    'status': {'name': 'In Progress'},
                    'updated': '2026-02-19T10:00:00.000+0000',
                    'priority': {'name': 'High'},
                    'comment': {'comments': []}
                },
                'self': 'https://test.atlassian.net/rest/api/3/issue/PROJ-123'
            }]
        }
        mock_get.return_value = mock_response

        source = JiraSource(jira_config, sample_persona)
        items = source.extract()
        assert len(items) == 1
        assert 'PROJ-123' in items[0]['content']
        assert items[0]['metadata']['status'] == 'In Progress'
        assert items[0]['url'] == 'https://daybreakers.atlassian.net/browse/PROJ-123'

    @patch('sources.jira_source.requests.get')
    def test_deduplicates_across_queries(self, mock_get, jira_config, sample_persona):
        """Same ticket from assignee query and project query should appear once."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'issues': [{
                'key': 'PROJ-123',
                'fields': {
                    'summary': 'Fix the login bug',
                    'assignee': {'displayName': 'Test User'},
                    'reporter': {'displayName': 'Boss'},
                    'status': {'name': 'In Progress'},
                    'priority': {'name': 'High'},
                    'comment': {'comments': []}
                }
            }]
        }
        mock_get.return_value = mock_response

        source = JiraSource(jira_config, sample_persona)
        items = source.extract()
        # Both queries return same ticket — should deduplicate to 1
        assert len(items) == 1

    @patch('sources.jira_source.requests.get')
    def test_extracts_adf_comments(self, mock_get, jira_config, sample_persona):
        """ADF-format comments should be converted to plain text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'issues': [{
                'key': 'PROJ-456',
                'fields': {
                    'summary': 'Review spec',
                    'assignee': None,
                    'reporter': {'displayName': 'Boss'},
                    'status': {'name': 'To Do'},
                    'priority': {'name': 'Medium'},
                    'comment': {'comments': [{
                        'author': {'displayName': 'Reviewer'},
                        'body': {
                            'type': 'doc',
                            'content': [{'type': 'paragraph', 'content': [
                                {'type': 'text', 'text': 'Please review this ASAP'}
                            ]}]
                        }
                    }]}
                }
            }]
        }
        mock_get.return_value = mock_response

        source = JiraSource(jira_config, sample_persona)
        items = source.extract()
        assert len(items) == 1
        assert 'Please review this ASAP' in items[0]['content']
        assert items[0]['metadata']['assignee'] == 'Unassigned'

    @patch('sources.jira_source.requests.get')
    def test_handles_api_error(self, mock_get, jira_config, sample_persona):
        mock_get.side_effect = Exception("Connection error")
        source = JiraSource(jira_config, sample_persona)
        items = source.extract()
        assert len(items) == 0

    @patch('sources.jira_source.requests.get')
    def test_handles_non_200_response(self, mock_get, jira_config, sample_persona):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_get.return_value = mock_response

        source = JiraSource(jira_config, sample_persona)
        items = source.extract()
        assert len(items) == 0
