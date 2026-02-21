import pytest
from unittest.mock import patch, MagicMock
from engine.ai_processor import AIProcessor


@pytest.fixture
def ai_config():
    return {
        'provider': 'anthropic',
        'api_key': 'test-key',
        'model': 'claude-sonnet-4-5-20250929',
        'confidence_threshold': 0.7
    }


class TestAIProcessor:
    def test_builds_prompt_with_persona_identity(self, ai_config, sample_persona):
        processor = AIProcessor(ai_config, sample_persona)
        item = {
            'content': 'Hey Test User, can you review the spec?',
            'author': 'Boss',
            'timestamp': '2026-02-19',
            'source_type': 'slack'
        }
        prompt = processor._build_extraction_prompt(item)
        assert 'Test User' in prompt
        assert 'TU' in prompt or 'test.user' in prompt  # aliases
        assert 'review the spec' in prompt

    def test_parses_valid_json_response(self, ai_config, sample_persona):
        processor = AIProcessor(ai_config, sample_persona)
        response_text = '''Here are the action items:
```json
[
  {
    "title": "Review the spec",
    "requestor": "Boss",
    "context": "Needs review before grooming",
    "due_date": "2026-02-20",
    "priority": "high",
    "project": "main",
    "confidence": 0.9
  }
]
```'''
        tasks = processor._parse_response(response_text)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Review the spec'

    def test_filters_low_confidence(self, ai_config, sample_persona):
        processor = AIProcessor(ai_config, sample_persona)
        response_text = '''[
  {"title": "High confidence", "confidence": 0.9, "requestor": "", "context": "", "due_date": null, "priority": "high", "project": ""},
  {"title": "Low confidence", "confidence": 0.3, "requestor": "", "context": "", "due_date": null, "priority": "low", "project": ""}
]'''
        tasks = processor._parse_response(response_text)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'High confidence'

    def test_handles_empty_response(self, ai_config, sample_persona):
        processor = AIProcessor(ai_config, sample_persona)
        tasks = processor._parse_response("No action items found.")
        assert tasks == []

    def test_handles_malformed_json(self, ai_config, sample_persona):
        processor = AIProcessor(ai_config, sample_persona)
        tasks = processor._parse_response("[{broken json")
        assert tasks == []

    @patch('engine.ai_processor.anthropic.Anthropic')
    def test_extract_calls_api(self, MockAnthropic, ai_config, sample_persona):
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='[{"title": "Test task", "requestor": "Boss", "context": "", "due_date": null, "priority": "high", "project": "main", "confidence": 0.9}]')]
        mock_client.messages.create.return_value = mock_response

        processor = AIProcessor(ai_config, sample_persona)
        items = [{'content': 'Please review spec', 'author': 'Boss', 'timestamp': '2026-02-19', 'source_type': 'slack', 'url': '', 'metadata': {}}]

        tasks = processor.extract_action_items(items)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Test task'
        mock_client.messages.create.assert_called_once()

    @patch('engine.ai_processor.anthropic.Anthropic')
    def test_adds_source_metadata(self, MockAnthropic, ai_config, sample_persona):
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='[{"title": "Test", "requestor": "", "context": "", "due_date": null, "priority": "medium", "project": "", "confidence": 0.9}]')]
        mock_client.messages.create.return_value = mock_response

        processor = AIProcessor(ai_config, sample_persona)
        items = [{
            'content': 'Test content',
            'author': 'Boss',
            'timestamp': '2026-02-19',
            'url': 'https://slack.com/msg',
            'source_type': 'slack',
            'metadata': {'channel': '#general'}
        }]

        tasks = processor.extract_action_items(items)
        assert tasks[0]['source_url'] == 'https://slack.com/msg'
        assert tasks[0]['source_author'] == 'Boss'
        assert tasks[0]['source_type'] == 'slack'
