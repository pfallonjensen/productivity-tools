"""
Google Docs source plugin — reads document content as action item candidates.
Uses GoogleAuthManager for authentication.
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sources.base_source import BaseSource


class GoogleDocsSource(BaseSource):
    """Scan Google Docs for action items."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.document_id = source_config.get('document_id', '')
        self.tab = source_config.get('tab', 'latest')
        self.lookback_hours = source_config.get('lookback_hours', 168)
        self.section_delimiter = source_config.get('section_delimiter', '---')
        self._auth_manager = None
        self._google_config = source_config.get('_google_config', {})

    def _get_auth_manager(self):
        """Lazy-init GoogleAuthManager."""
        if self._auth_manager is None:
            from engine.google_auth import GoogleAuthManager
            self._auth_manager = GoogleAuthManager(self._google_config)
        return self._auth_manager

    def extract(self) -> List[Dict]:
        """Extract content sections from a Google Doc."""
        if not self.is_available():
            self.logger.info("Google Docs source not available — skipping")
            return []

        try:
            service = self._get_auth_manager().get_service('docs', 'v1')

            # Fetch the document
            doc = service.documents().get(documentId=self.document_id).execute()
            title = doc.get('title', 'Untitled Document')

            # Extract plain text from document body
            body = doc.get('body', {})
            content = self._extract_text(body)

            if not content.strip():
                self.logger.info(f"Document '{title}' is empty")
                return []

            # Check document modification time via Drive API
            mod_time = self._get_modification_time()
            if mod_time and not self.is_within_lookback(mod_time, self.lookback_hours):
                self.logger.info(f"Document '{title}' not modified within lookback period")
                return []

            # Split content into sections
            sections = self._split_into_sections(content)
            self.logger.info(f"Extracted {len(sections)} sections from '{title}'")

            items = []
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                items.append({
                    'content': section.strip(),
                    'author': title,
                    'timestamp': mod_time or datetime.now(),
                    'url': f"https://docs.google.com/document/d/{self.document_id}",
                    'metadata': {
                        'source_type': 'google_docs',
                        'document_id': self.document_id,
                        'document_title': title,
                        'section_index': i,
                    }
                })

            return items

        except Exception as e:
            self.logger.error(f"Error reading Google Doc: {e}")
            return []

    def _extract_text(self, body: dict) -> str:
        """Extract plain text from Google Docs body structure."""
        text_parts = []
        for element in body.get('content', []):
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    text_run = elem.get('textRun', {})
                    text = text_run.get('content', '')
                    if text:
                        text_parts.append(text)
            elif 'table' in element:
                # Extract text from table cells
                table = element['table']
                for row in table.get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        cell_content = cell.get('content', [])
                        for cell_elem in cell_content:
                            if 'paragraph' in cell_elem:
                                for elem in cell_elem['paragraph'].get('elements', []):
                                    text = elem.get('textRun', {}).get('content', '')
                                    if text:
                                        text_parts.append(text)
                        text_parts.append('\t')
                    text_parts.append('\n')
        return ''.join(text_parts)

    def _split_into_sections(self, content: str) -> List[str]:
        """Split document content into logical sections."""
        if self.section_delimiter:
            sections = content.split(self.section_delimiter)
            # Filter out very short sections (likely just whitespace)
            sections = [s for s in sections if len(s.strip()) > 20]
            if sections:
                return sections

        # Fallback: split by double newlines into paragraph groups
        paragraphs = content.split('\n\n')
        sections = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) > 1000 and current:
                sections.append(current)
                current = para
            else:
                current = f"{current}\n\n{para}" if current else para
        if current.strip():
            sections.append(current)

        return sections

    def _get_modification_time(self) -> Optional[datetime]:
        """Get document modification time via Drive API."""
        try:
            drive_service = self._get_auth_manager().get_service('drive', 'v3')
            file_meta = drive_service.files().get(
                fileId=self.document_id,
                fields='modifiedTime'
            ).execute()
            mod_str = file_meta.get('modifiedTime', '')
            if mod_str:
                # Google returns ISO format: 2026-02-20T10:30:00.000Z
                return datetime.fromisoformat(mod_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except Exception as e:
            self.logger.debug(f"Could not get modification time: {e}")
        return None

    def is_available(self) -> bool:
        """Check if Google Docs source is configured and authenticated."""
        if not self.document_id:
            return False
        try:
            return self._get_auth_manager().is_authenticated()
        except Exception:
            return False
