import pytest
from engine.dedup import Deduplicator


class TestDeduplicator:
    def test_exact_duplicate_removed(self):
        dedup = Deduplicator()
        tasks = [
            {"title": "Review the spec", "source": "slack", "content": "Review the spec for DDS"},
            {"title": "Review the spec", "source": "meeting", "content": "Review the spec for DDS"}
        ]
        result = dedup.deduplicate(tasks)
        assert len(result) == 1

    def test_fuzzy_duplicate_removed(self):
        dedup = Deduplicator(threshold=0.8)
        tasks = [
            {"title": "Review the DDS spec by Friday", "source": "slack", "content": ""},
            {"title": "Review DDS spec by Friday", "source": "meeting", "content": ""}
        ]
        result = dedup.deduplicate(tasks)
        assert len(result) == 1

    def test_different_tasks_kept(self):
        dedup = Deduplicator(threshold=0.8)
        tasks = [
            {"title": "Review the spec", "source": "slack", "content": ""},
            {"title": "Update the roadmap", "source": "meeting", "content": ""}
        ]
        result = dedup.deduplicate(tasks)
        assert len(result) == 2

    def test_fingerprint_dedup(self):
        dedup = Deduplicator()
        tasks = [
            {"title": "Follow up with Tim", "source": "slack", "content": "Follow up with Tim on pricing"},
            {"title": "Follow up with Tim", "source": "slack", "content": "Follow up with Tim on pricing"}
        ]
        result = dedup.deduplicate(tasks)
        assert len(result) == 1

    def test_empty_list(self):
        dedup = Deduplicator()
        assert dedup.deduplicate([]) == []

    def test_single_item(self):
        dedup = Deduplicator()
        tasks = [{"title": "Solo task", "source": "slack", "content": ""}]
        result = dedup.deduplicate(tasks)
        assert len(result) == 1

    def test_threshold_respected(self):
        """With high threshold, similar but different titles are kept"""
        dedup = Deduplicator(threshold=0.95)
        tasks = [
            {"title": "Review the DDS spec", "source": "slack", "content": ""},
            {"title": "Review the DDS roadmap", "source": "meeting", "content": ""}
        ]
        result = dedup.deduplicate(tasks)
        assert len(result) == 2

    def test_is_duplicate_of_existing(self):
        """Check a single task against a list of existing tasks"""
        dedup = Deduplicator(threshold=0.75)
        existing = [
            {"title": "Review the spec"},
            {"title": "Update the roadmap"}
        ]
        assert dedup.is_duplicate_of_existing("Review the spec for DDS", existing) is True
        assert dedup.is_duplicate_of_existing("Completely new task", existing) is False
