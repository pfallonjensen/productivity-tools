import pytest
import os
import time
from sources.local_files_source import LocalFilesSource


class TestLocalFilesSource:
    def test_finds_recent_txt_files(self, tmp_path, sample_config, sample_persona):
        transcript = tmp_path / "Meeting - 2026 02 19 - Notes.txt"
        transcript.write_text("Test User committed to review the spec by Friday.")

        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)

        source = LocalFilesSource(source_config, sample_persona)
        items = source.extract()
        assert len(items) == 1
        assert "review the spec" in items[0]['content']

    def test_skips_old_files(self, tmp_path, sample_config, sample_persona):
        transcript = tmp_path / "Old Meeting.txt"
        transcript.write_text("Test User needs to do something")
        old_time = time.time() - (7 * 24 * 3600)
        os.utime(transcript, (old_time, old_time))

        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)
        source_config['lookback_hours'] = 48

        source = LocalFilesSource(source_config, sample_persona)
        items = source.extract()
        assert len(items) == 0

    def test_returns_standard_item_structure(self, tmp_path, sample_config, sample_persona):
        transcript = tmp_path / "Standup.txt"
        transcript.write_text("Test User will follow up on the design review")

        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)

        source = LocalFilesSource(source_config, sample_persona)
        items = source.extract()
        item = items[0]
        assert 'content' in item
        assert 'author' in item
        assert 'timestamp' in item
        assert 'url' in item
        assert 'metadata' in item

    def test_matches_file_patterns(self, tmp_path, sample_config, sample_persona):
        txt_file = tmp_path / "meeting.txt"
        txt_file.write_text("Test User has a task from the txt meeting")
        md_file = tmp_path / "notes.md"
        md_file.write_text("Test User has a task from the md notes")
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("Test User has a task from csv data")

        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)
        source_config['file_patterns'] = ['*.txt', '*.md']

        source = LocalFilesSource(source_config, sample_persona)
        items = source.extract()
        assert len(items) == 2  # csv should be skipped

    def test_is_available_with_existing_path(self, tmp_path, sample_config, sample_persona):
        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)
        source = LocalFilesSource(source_config, sample_persona)
        assert source.is_available() is True

    def test_is_available_with_missing_path(self, sample_config, sample_persona):
        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = '/nonexistent/path'
        source = LocalFilesSource(source_config, sample_persona)
        assert source.is_available() is False

    def test_parses_meeting_name_from_filename(self, tmp_path, sample_config, sample_persona):
        transcript = tmp_path / "DDS Grooming - 2026 02 19 - Notes.txt"
        transcript.write_text("Test User should follow up on grooming items")

        source_config = {**sample_config['sources']['meetings']}
        source_config['path'] = str(tmp_path)

        source = LocalFilesSource(source_config, sample_persona)
        items = source.extract()
        assert items[0]['metadata']['meeting_name'] == 'DDS Grooming'
