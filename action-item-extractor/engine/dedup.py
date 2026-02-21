"""
Deduplication engine — prevents duplicate action items using fingerprint and fuzzy matching.
Uses difflib.SequenceMatcher (no external deps).
"""
import hashlib
from difflib import SequenceMatcher
from typing import List


class Deduplicator:
    """Deduplicates tasks using fingerprint matching and fuzzy title similarity."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def deduplicate(self, tasks: List[dict]) -> List[dict]:
        """
        Remove duplicate tasks from a list.

        Checks:
        1. Exact fingerprint match (hash of title + content)
        2. Fuzzy title match (SequenceMatcher ratio >= threshold)
        """
        if not tasks:
            return []

        seen_fingerprints = set()
        kept_titles = []
        result = []

        for task in tasks:
            # 1. Fingerprint check
            fp = self._fingerprint(task)
            if fp in seen_fingerprints:
                continue

            # 2. Fuzzy title check
            title = task.get("title", "")
            if self._fuzzy_match_any(title, kept_titles):
                continue

            seen_fingerprints.add(fp)
            kept_titles.append(title)
            result.append(task)

        return result

    def is_duplicate_of_existing(self, title: str, existing_tasks: List[dict]) -> bool:
        """Check if a title is a duplicate of any existing task."""
        existing_titles = [t.get("title", "") for t in existing_tasks]
        return self._fuzzy_match_any(title, existing_titles)

    def _fingerprint(self, task: dict) -> str:
        """Create a content-based fingerprint for exact matching."""
        key = f"{task.get('title', '')}|{task.get('content', '')}".lower().strip()
        return hashlib.md5(key.encode()).hexdigest()

    def _fuzzy_match_any(self, title: str, existing_titles: List[str]) -> bool:
        """Check if title fuzzy-matches any existing title."""
        title_lower = title.lower().strip()
        for existing in existing_titles:
            existing_lower = existing.lower().strip()
            ratio = SequenceMatcher(None, title_lower, existing_lower).ratio()
            if ratio >= self.threshold:
                return True
        return False
