"""
CSV output plugin — saves tasks as a CSV file for spreadsheet import.
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from outputs.base_output import BaseOutput


CSV_COLUMNS = [
    'title', 'priority', 'due_date', 'requestor', 'project',
    'context', 'source_type', 'source_url', 'confidence'
]


class CsvOutput(BaseOutput):
    """Save tasks as CSV files."""

    def __init__(self, output_config: dict, persona: dict):
        super().__init__(output_config, persona)
        self.path = Path(output_config.get('path', '.'))

    def save_tasks(self, tasks: List[Dict]) -> None:
        if not tasks:
            return

        today = datetime.now().strftime('%Y-%m-%d')
        output_file = self.path / f"{today}-action-items.csv"

        self.path.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for task in tasks:
                row = [task.get(col, '') for col in CSV_COLUMNS]
                writer.writerow(row)

    def update_dashboard(self) -> None:
        pass
