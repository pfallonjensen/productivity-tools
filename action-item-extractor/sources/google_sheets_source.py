"""
Google Sheets source plugin — reads rows from a spreadsheet as action item candidates.
Uses GoogleAuthManager for authentication.
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sources.base_source import BaseSource


class GoogleSheetsSource(BaseSource):
    """Scan Google Sheets for action items."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.spreadsheet_id = source_config.get('spreadsheet_id', '')
        self.sheet_name = source_config.get('sheet_name', 'Sheet1')
        self.content_columns = source_config.get('content_columns', ['A', 'B'])
        self.author_column = source_config.get('author_column', '')
        self.timestamp_column = source_config.get('timestamp_column', '')
        self.lookback_hours = source_config.get('lookback_hours', 168)
        self._auth_manager = None
        self._google_config = source_config.get('_google_config', {})

    def _get_auth_manager(self):
        """Lazy-init GoogleAuthManager."""
        if self._auth_manager is None:
            from engine.google_auth import GoogleAuthManager
            self._auth_manager = GoogleAuthManager(self._google_config)
        return self._auth_manager

    def extract(self) -> List[Dict]:
        """Extract rows from Google Sheets as action item candidates."""
        if not self.is_available():
            self.logger.info("Google Sheets source not available — skipping")
            return []

        try:
            service = self._get_auth_manager().get_service('sheets', 'v4')
            sheets = service.spreadsheets()

            # Build range from content columns
            all_columns = list(self.content_columns)
            if self.author_column and self.author_column not in all_columns:
                all_columns.append(self.author_column)
            if self.timestamp_column and self.timestamp_column not in all_columns:
                all_columns.append(self.timestamp_column)

            # Sort columns alphabetically to build a contiguous range
            sorted_cols = sorted(all_columns)
            range_str = f"'{self.sheet_name}'!{sorted_cols[0]}:{sorted_cols[-1]}"

            result = sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
            ).execute()

            rows = result.get('values', [])
            if not rows:
                self.logger.info("No data found in spreadsheet")
                return []

            # First row is headers
            headers = rows[0]
            items = []

            for row in rows[1:]:
                item = self._row_to_item(row, headers, sorted_cols)
                if item:
                    items.append(item)

            self.logger.info(f"Extracted {len(items)} items from Google Sheets")
            return items

        except Exception as e:
            self.logger.error(f"Error reading Google Sheets: {e}")
            return []

    def _row_to_item(self, row: list, headers: list, sorted_cols: list) -> Optional[Dict]:
        """Convert a spreadsheet row to a RawItem dict."""
        # Pad row to match headers length
        while len(row) < len(headers):
            row.append('')

        # Build column-to-value mapping
        col_values = {}
        for i, header in enumerate(headers):
            col_letter = sorted_cols[i] if i < len(sorted_cols) else chr(ord('A') + i)
            col_values[col_letter] = row[i] if i < len(row) else ''

        # Extract content from configured columns
        content_parts = []
        for col in self.content_columns:
            val = col_values.get(col, '')
            if val:
                content_parts.append(str(val))

        content = ' | '.join(content_parts)
        if not content.strip():
            return None

        # Extract author
        author = 'Spreadsheet'
        if self.author_column:
            author = col_values.get(self.author_column, 'Spreadsheet') or 'Spreadsheet'

        # Extract timestamp
        timestamp = datetime.now()
        if self.timestamp_column:
            ts_str = col_values.get(self.timestamp_column, '')
            if ts_str:
                timestamp = self._parse_timestamp(ts_str) or timestamp

        # Check lookback
        if not self.is_within_lookback(timestamp, self.lookback_hours):
            return None

        return {
            'content': content,
            'author': str(author),
            'timestamp': timestamp,
            'url': f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}",
            'metadata': {
                'source_type': 'google_sheets',
                'spreadsheet_id': self.spreadsheet_id,
                'sheet_name': self.sheet_name,
            }
        }

    @staticmethod
    def _parse_timestamp(ts_str: str) -> Optional[datetime]:
        """Try to parse a timestamp string in common formats."""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y',
            '%d/%m/%Y',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def is_available(self) -> bool:
        """Check if Google Sheets source is configured and authenticated."""
        if not self.spreadsheet_id:
            return False
        try:
            return self._get_auth_manager().is_authenticated()
        except Exception:
            return False
