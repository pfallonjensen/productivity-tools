"""
Jira source plugin -- scans Jira tickets assigned to or mentioning the user.
"""
import base64
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from sources.base_source import BaseSource


class JiraSource(BaseSource):
    """Scan Jira for recently updated tickets."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.cloud_id = source_config.get('cloud_id', '')
        self.token = source_config.get('token', '')
        self.email = source_config.get('email', '')
        self.site = source_config.get('site', 'daybreakers')
        self.lookback_days = source_config.get('lookback_days', 7)
        self.projects = source_config.get('projects', [])

    def _auth_header(self) -> str:
        """Atlassian Cloud REST API uses Basic auth: base64(email:api_token)."""
        credentials = base64.b64encode(f"{self.email}:{self.token}".encode()).decode()
        return f"Basic {credentials}"

    def extract(self) -> List[Dict]:
        if not self.is_available():
            return []

        items = []
        user_name = self.persona.get('identity', {}).get('name', '')
        since = (datetime.now() - timedelta(days=self.lookback_days)).strftime('%Y-%m-%d')

        # Build JQL — v3 /search/jql requires bounded queries
        # Run two queries: assigned tickets + mentioned tickets per project
        queries = []
        queries.append(f'assignee = currentUser() AND updated >= "{since}" ORDER BY updated DESC')
        for proj in self.projects:
            queries.append(
                f'project = {proj} AND updated >= "{since}" AND text ~ "{user_name}" ORDER BY updated DESC'
            )

        seen_keys = set()
        for jql in queries:
            try:
                response = requests.get(
                    f'https://{self.site}.atlassian.net/rest/api/3/search/jql',
                    headers={
                        'Authorization': self._auth_header(),
                        'Accept': 'application/json'
                    },
                    params={
                        'jql': jql,
                        'maxResults': 50,
                        'fields': 'summary,status,priority,assignee,reporter,updated,comment'
                    }
                )
                if response.status_code != 200:
                    self.logger.warning(f"Jira query returned {response.status_code}: {response.text[:200]}")
                    continue

                data = response.json()

                for issue in data.get('issues', []):
                    key = issue.get('key', '')
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    fields = issue.get('fields', {})
                    summary = fields.get('summary', '')
                    reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
                    assignee = fields.get('assignee', {})
                    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
                    status = fields.get('status', {}).get('name', '')

                    # Build content with recent comments
                    content_parts = [f"{key}: {summary}", f"Status: {status}", f"Assignee: {assignee_name}"]
                    comments = fields.get('comment', {}).get('comments', [])
                    if comments:
                        recent = comments[-3:]  # last 3 comments
                        for c in recent:
                            author = c.get('author', {}).get('displayName', '?')
                            body = c.get('body', '')
                            if isinstance(body, dict):
                                # ADF format — extract text content
                                body = self._extract_adf_text(body)
                            content_parts.append(f"Comment by {author}: {body[:500]}")

                    items.append({
                        'content': '\n'.join(content_parts),
                        'author': reporter,
                        'timestamp': datetime.now(),
                        'url': f"https://{self.site}.atlassian.net/browse/{key}",
                        'metadata': {
                            'source_type': 'jira',
                            'ticket_key': key,
                            'status': status,
                            'priority': fields.get('priority', {}).get('name', ''),
                            'assignee': assignee_name
                        }
                    })

            except Exception as e:
                self.logger.error(f"Error extracting from Jira: {e}")

        return items

    @staticmethod
    def _extract_adf_text(adf: dict) -> str:
        """Extract plain text from Atlassian Document Format (ADF) JSON."""
        texts = []
        for node in adf.get('content', []):
            for child in node.get('content', []):
                if child.get('type') == 'text':
                    texts.append(child.get('text', ''))
        return ' '.join(texts)

    def is_available(self) -> bool:
        return bool(self.cloud_id and self.token and self.email)
