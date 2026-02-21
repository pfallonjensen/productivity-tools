"""
Local files source plugin — scans a directory for transcript files.
"""
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from sources.base_source import BaseSource


class LocalFilesSource(BaseSource):
    """Scan local files (meeting transcripts, notes) for action items."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.path = Path(source_config.get('path', ''))
        self.file_patterns = source_config.get('file_patterns', ['*.txt', '*.md'])
        self.lookback_hours = source_config.get('lookback_hours', 48)

    def extract(self) -> List[Dict]:
        """Extract content from recent local files."""
        if not self.is_available():
            self.logger.warning(f"Source path not found: {self.path}")
            return []

        items = []
        for file_path in self.path.iterdir():
            if not file_path.is_file():
                continue

            # Check file pattern match
            if not any(fnmatch.fnmatch(file_path.name, pat) for pat in self.file_patterns):
                continue

            # Check recency
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if not self.is_within_lookback(mod_time, self.lookback_hours):
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")
                continue

            meeting_name = self._parse_meeting_name(file_path.name)

            items.append({
                'content': content,
                'author': 'Meeting Participants',
                'timestamp': mod_time,
                'url': f"file://{file_path}",
                'metadata': {
                    'source_type': 'local_files',
                    'meeting_name': meeting_name,
                    'file_name': file_path.name,
                    'file_path': str(file_path)
                }
            })

        return items

    def is_available(self) -> bool:
        """Check if the source directory exists."""
        return self.path.exists() and self.path.is_dir()

    @staticmethod
    def _parse_meeting_name(filename: str) -> str:
        """Extract meeting name from filename. Expects 'Name - Date - Notes.ext' format."""
        parts = filename.split(' - ')
        if parts:
            return parts[0]
        stem = Path(filename).stem
        return stem
