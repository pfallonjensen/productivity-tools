"""
Slack source plugin -- scans DMs, group DMs, and channels for action items.
Config-driven: token, workspace, channels from config. No hardcoded values.
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from sources.base_source import BaseSource


class SlackSource(BaseSource):
    """Scan Slack DMs and channels for action items."""

    def __init__(self, source_config: dict, persona: dict):
        super().__init__(source_config, persona)
        self.token = source_config.get('token', '')
        self.workspace = source_config.get('workspace', '')
        self.user_id = source_config.get(
            'user_id',
            persona.get('identity', {}).get('slack_user_id', '')
        )
        self.lookback_hours = source_config.get('lookback_hours', 24)
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        # Cache user names to reduce API calls
        self._user_cache = {}

    def extract(self) -> List[Dict]:
        """Extract messages from Slack DMs and channels."""
        if not self.is_available():
            return []

        oldest = (datetime.now() - timedelta(hours=self.lookback_hours)).timestamp()
        items = []

        try:
            items.extend(self._extract_dms(oldest))
        except Exception as e:
            self.logger.error(f"Error extracting Slack DMs: {e}")

        try:
            items.extend(self._extract_channels(oldest))
        except Exception as e:
            self.logger.error(f"Error extracting Slack channels: {e}")

        return items

    def is_available(self) -> bool:
        """Check if Slack token is configured."""
        return bool(self.token)

    def _extract_dms(self, oldest: float) -> List[Dict]:
        """Extract from direct messages."""
        items = []

        response = requests.get(
            'https://slack.com/api/conversations.list',
            headers=self.headers,
            params={'types': 'im', 'limit': 1000}
        )
        data = response.json()

        if not data.get('ok'):
            self.logger.error(f"Slack API error: {data.get('error')}")
            return items

        for channel in data.get('channels', []):
            channel_id = channel['id']
            messages = self._get_channel_history(channel_id, oldest)

            for msg in messages:
                if msg.get('user') == self.user_id:
                    continue
                items.append(self._format_message(msg, channel, 'DM'))

        return items

    def _extract_channels(self, oldest: float) -> List[Dict]:
        """Extract from configured channels."""
        items = []
        # Get channel IDs from persona projects
        channel_ids = set()
        for proj in self.persona.get('projects', {}).values():
            channel_ids.update(proj.get('channels', []))

        if not channel_ids:
            return items

        for channel_id in channel_ids:
            messages = self._get_channel_history(channel_id, oldest)
            channel_info = {'id': channel_id, 'name': channel_id}

            for msg in messages:
                if msg.get('user') == self.user_id:
                    continue
                items.append(self._format_message(msg, channel_info, 'Channel'))

        return items

    def _get_channel_history(self, channel_id: str, oldest: float) -> List[Dict]:
        """Get message history for a channel."""
        try:
            response = requests.get(
                'https://slack.com/api/conversations.history',
                headers=self.headers,
                params={'channel': channel_id, 'oldest': oldest, 'limit': 1000}
            )
            data = response.json()
            if data.get('ok'):
                return data.get('messages', [])
            else:
                self.logger.error(f"Error fetching {channel_id}: {data.get('error')}")
        except Exception as e:
            self.logger.error(f"Error getting channel history: {e}")
        return []

    def _format_message(self, msg: Dict, channel: Dict, msg_type: str) -> Dict:
        """Format a Slack message into standard item structure."""
        ts = msg.get('ts', '0')
        timestamp = datetime.fromtimestamp(float(ts))
        user_name = self._get_user_name(msg.get('user', ''))
        channel_id = channel['id']
        thread_ts = msg.get('thread_ts', ts)
        slack_url = (
            f"https://{self.workspace}.slack.com/archives/"
            f"{channel_id}/p{thread_ts.replace('.', '')}"
        )

        return {
            'content': msg.get('text', ''),
            'author': user_name,
            'timestamp': timestamp,
            'url': slack_url,
            'metadata': {
                'source_type': 'slack',
                'message_type': msg_type,
                'channel_name': channel.get('name', 'DM'),
                'channel_id': channel_id,
                'has_thread': 'thread_ts' in msg,
            }
        }

    def _get_user_name(self, user_id: str) -> str:
        """Get display name for a Slack user ID (cached)."""
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        try:
            response = requests.get(
                'https://slack.com/api/users.info',
                headers=self.headers,
                params={'user': user_id}
            )
            data = response.json()
            if data.get('ok'):
                name = (
                    data['user'].get('real_name')
                    or data['user'].get('name', user_id)
                )
                self._user_cache[user_id] = name
                return name
        except Exception as e:
            self.logger.error(f"Error getting user info: {e}")
        self._user_cache[user_id] = user_id
        return user_id
