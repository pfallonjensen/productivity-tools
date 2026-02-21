"""
Confluence source plugin -- scans recently updated pages mentioning the user.
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from sources.base_source import BaseSource


class ConfluenceSource(BaseSource):
    """Scan Confluence for recently updated pages."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.cloud_id = source_config.get('cloud_id', '')
        self.token = source_config.get('token', '')
        self.lookback_days = source_config.get('lookback_days', 7)

    def extract(self) -> List[Dict]:
        if not self.is_available():
            return []

        items = []
        user_name = self.persona.get('identity', {}).get('name', '')

        try:
            response = requests.get(
                f'https://api.atlassian.com/ex/confluence/{self.cloud_id}/wiki/rest/api/content',
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Accept': 'application/json'
                },
                params={
                    'cql': f'text ~ "{user_name}" AND lastModified > now("-{self.lookback_days}d")',
                    'limit': 50,
                    'expand': 'body.storage,version'
                }
            )
            data = response.json()

            for page in data.get('results', []):
                title = page.get('title', '')
                body = page.get('body', {}).get('storage', {}).get('value', '')
                version = page.get('version', {})
                modified_by = version.get('by', {}).get('displayName', 'Unknown')

                items.append({
                    'content': f"{title}\n{body[:2000]}",
                    'author': modified_by,
                    'timestamp': datetime.now(),
                    'url': page.get('_links', {}).get('webui', ''),
                    'metadata': {
                        'source_type': 'confluence',
                        'page_title': title,
                        'page_id': page.get('id', '')
                    }
                })

        except Exception as e:
            self.logger.error(f"Error extracting from Confluence: {e}")

        return items

    def is_available(self) -> bool:
        return bool(self.cloud_id and self.token)
