import pytest
import csv
from datetime import datetime
from pathlib import Path
from outputs.csv_output import CsvOutput


@pytest.fixture
def csv_config(tmp_path):
    return {
        'type': 'csv',
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
        },
        {
            'title': 'Update roadmap',
            'requestor': 'CEO',
            'context': 'Q1 planning',
            'due_date': today,
            'priority': 'medium',
            'project': 'company',
            'source_url': '',
            'source_author': 'CEO',
            'source_type': 'meeting',
            'source_timestamp': today,
            'confidence': 0.85
        }
    ]


class TestCsvOutput:
    def test_creates_csv_file(self, csv_config, sample_persona, sample_tasks, tmp_path):
        output = CsvOutput(csv_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        csv_file = tmp_path / f"{today}-action-items.csv"
        assert csv_file.exists()

    def test_csv_has_headers(self, csv_config, sample_persona, sample_tasks, tmp_path):
        output = CsvOutput(csv_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        csv_file = tmp_path / f"{today}-action-items.csv"

        with open(csv_file) as f:
            reader = csv.reader(f)
            headers = next(reader)
            assert 'title' in headers
            assert 'priority' in headers
            assert 'due_date' in headers

    def test_csv_has_correct_row_count(self, csv_config, sample_persona, sample_tasks, tmp_path):
        output = CsvOutput(csv_config, sample_persona)
        output.save_tasks(sample_tasks)

        today = datetime.now().strftime('%Y-%m-%d')
        csv_file = tmp_path / f"{today}-action-items.csv"

        with open(csv_file) as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 3  # header + 2 tasks

    def test_empty_tasks_no_crash(self, csv_config, sample_persona, tmp_path):
        output = CsvOutput(csv_config, sample_persona)
        output.save_tasks([])
