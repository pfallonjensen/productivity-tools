"""
Config loader — reads persona.yaml and config.yaml, provides accessors.
"""
import os
import re
import yaml
from pathlib import Path
from typing import Optional


class ConfigLoader:
    """Loads persona + config and provides helper methods for the extraction engine."""

    def __init__(self, persona_path: str, config_path: Optional[str] = None):
        self.persona = self._load_yaml(persona_path)
        self.config = self._load_yaml(config_path) if config_path else {}

        identity = self.persona.get('identity', {})
        self.user_name = identity.get('name', '')
        self.user_aliases = identity.get('aliases', [])
        self.slack_user_id = identity.get('slack_user_id', '')
        self.role = identity.get('role', '')

        self.projects = self.persona.get('projects', {})
        self.priority_contacts = self.persona.get('priority_contacts', [])
        self.themes = self.persona.get('themes', {})
        self.skip_keywords = self.persona.get('skip_keywords', [])
        self.ticket_detection = self.persona.get('ticket_detection', {})

        # Build lookup structures
        self._channel_to_project = {}
        self._keyword_to_project = {}
        for proj_key, proj in self.projects.items():
            for ch in proj.get('channels', []):
                self._channel_to_project[ch] = proj_key
            for kw in proj.get('detect_keywords', []):
                self._keyword_to_project[kw.lower()] = proj_key

        self._priority_usernames = {
            c['username'].lower() for c in self.priority_contacts
        }

    @staticmethod
    def _load_yaml(path: str) -> dict:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(p) as f:
            raw = f.read()
        # Expand ${ENV_VAR} references before YAML parsing
        expanded = ConfigLoader._expand_env_vars(raw)
        return yaml.safe_load(expanded) or {}

    @staticmethod
    def _expand_env_vars(text: str) -> str:
        """Replace ${VAR} and $VAR with environment variable values."""
        return os.path.expandvars(text)

    def detect_project(self, text: str, channel_id: Optional[str] = None) -> Optional[str]:
        """Detect which project a message relates to."""
        # 1. Channel match (highest confidence)
        if channel_id and channel_id in self._channel_to_project:
            return self._channel_to_project[channel_id]

        # 2. Keyword match
        text_lower = text.lower()
        for kw, proj_key in self._keyword_to_project.items():
            if kw in text_lower:
                return proj_key

        # 3. Default to first project
        if self.projects:
            return next(iter(self.projects))
        return None

    def is_priority_contact(self, username: str) -> bool:
        return username.lower() in self._priority_usernames

    def mentions_user(self, text: str) -> bool:
        """Check if text mentions the user by name, alias, or Slack ID."""
        text_lower = text.lower()
        identifiers = [self.user_name] + self.user_aliases
        if any(ident.lower() in text_lower for ident in identifiers):
            return True
        if self.slack_user_id and self.slack_user_id in text:
            return True
        return False
