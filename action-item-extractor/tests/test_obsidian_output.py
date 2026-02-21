import pytest
from datetime import datetime, timedelta
from pathlib import Path
from outputs.obsidian_output import ObsidianOutput


@pytest.fixture
def output_config(tmp_vault):
    return {
        'type': 'obsidian',
        'path': str(tmp_vault),
        'action_items_path': 'Action Items',
        'preserve_manual_priorities': True,
        'carry_forward_incomplete': True,
        'past_due_tracking': True
    }


@pytest.fixture
def sample_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    return [
        {
            'title': 'Review the DDS spec',
            'requestor': 'Boss Person',
            'context': 'Needs review before grooming',
            'due_date': today,
            'priority': 'high',
            'project': 'dds',
            'source_url': 'https://slack.com/archives/C123/p123',
            'source_author': 'Boss Person',
            'source_type': 'slack',
            'source_timestamp': today,
            'confidence': 0.9
        },
        {
            'title': 'Update the roadmap document',
            'requestor': 'CEO',
            'context': 'Q1 planning',
            'due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'priority': 'medium',
            'project': 'company',
            'source_url': 'https://slack.com/archives/C456/p456',
            'source_author': 'CEO',
            'source_type': 'slack',
            'source_timestamp': today,
            'confidence': 0.85
        }
    ]


class TestObsidianOutput:
    def test_creates_daily_file(self, tmp_vault, output_config, sample_persona, sample_tasks):
        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_vault / "Action Items" / f"{today} - Action Items.md"
        assert daily_file.exists()
        content = daily_file.read_text()
        assert 'Review the DDS spec' in content

    def test_preserves_manual_priorities(self, tmp_vault, output_config, sample_persona, sample_tasks):
        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_vault / "Action Items" / f"{today} - Action Items.md"
        daily_file.write_text("# My Chosen Priorities\n\n- [ ] My manual task\n- [ ] Another manual task\n\n---\n")

        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(sample_tasks)

        content = daily_file.read_text()
        assert 'My manual task' in content
        assert 'Another manual task' in content
        assert 'Review the DDS spec' in content

    def test_dedup_against_existing(self, tmp_vault, output_config, sample_persona, sample_tasks):
        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(sample_tasks)
        output.save_tasks(sample_tasks)  # Save again

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_vault / "Action Items" / f"{today} - Action Items.md"
        content = daily_file.read_text()
        # Should only appear once
        assert content.count('Review the DDS spec') == 1

    def test_task_format_includes_priority_emoji(self, tmp_vault, output_config, sample_persona, sample_tasks):
        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_vault / "Action Items" / f"{today} - Action Items.md"
        content = daily_file.read_text()
        assert '\u23eb' in content  # high priority emoji

    def test_past_due_indicator(self, tmp_vault, output_config, sample_persona):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        overdue_tasks = [{
            'title': 'Overdue task',
            'requestor': 'Someone',
            'context': 'Was due yesterday',
            'due_date': yesterday,
            'priority': 'high',
            'project': 'test',
            'source_url': '',
            'source_author': 'Someone',
            'source_type': 'slack',
            'source_timestamp': yesterday,
            'confidence': 0.9
        }]

        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(overdue_tasks)

        today_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = tmp_vault / "Action Items" / f"{today_str} - Action Items.md"
        content = daily_file.read_text()
        assert 'PAST DUE' in content or 'overdue' in content.lower()

    def test_source_files_created(self, tmp_vault, output_config, sample_persona, sample_tasks):
        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        slack_file = tmp_vault / "Action Items" / "By Source" / "From Slack" / f"{today}.md"
        assert slack_file.exists()

    def test_empty_tasks_no_crash(self, tmp_vault, output_config, sample_persona):
        output = ObsidianOutput(output_config, sample_persona)
        output.save_tasks([])  # Should not crash
