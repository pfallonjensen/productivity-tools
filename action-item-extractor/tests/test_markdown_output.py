import pytest
from datetime import datetime
from pathlib import Path
from outputs.markdown_output import MarkdownOutput


@pytest.fixture
def md_config(tmp_path):
    return {
        'type': 'markdown',
        'path': str(tmp_path),
    }


@pytest.fixture
def sample_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    return [
        {
            'title': 'Review the spec',
            'requestor': 'Boss',
            'context': 'Needs review',
            'due_date': today,
            'priority': 'high',
            'project': 'main',
            'source_url': 'https://example.com',
            'source_author': 'Boss',
            'source_type': 'slack',
            'source_timestamp': today,
            'confidence': 0.9
        }
    ]


class TestMarkdownOutput:
    def test_creates_daily_file(self, md_config, sample_persona, sample_tasks, tmp_path):
        output = MarkdownOutput(md_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_path / f"{today}-action-items.md"
        assert daily_file.exists()
        content = daily_file.read_text()
        assert 'Review the spec' in content

    def test_includes_priority(self, md_config, sample_persona, sample_tasks, tmp_path):
        output = MarkdownOutput(md_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_path / f"{today}-action-items.md"
        content = daily_file.read_text()
        assert 'high' in content.lower() or '\u23eb' in content

    def test_empty_tasks_no_crash(self, md_config, sample_persona, tmp_path):
        output = MarkdownOutput(md_config, sample_persona)
        output.save_tasks([])
