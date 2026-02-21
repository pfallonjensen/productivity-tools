import pytest
import yaml
from pathlib import Path
from engine.extractor import Extractor


@pytest.fixture
def setup_configs(tmp_path, sample_persona, sample_config):
    """Write config files and return paths."""
    persona_file = tmp_path / "persona.yaml"
    persona_file.write_text(yaml.dump(sample_persona))

    config_data = {**sample_config}
    # Point local_files source at a temp directory with a transcript
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    transcript = transcripts_dir / "Meeting - 2026 02 19 - Notes.txt"
    transcript.write_text("Test User committed to review the spec by Friday. Boss asked for roadmap update.")

    config_data['sources']['meetings']['path'] = str(transcripts_dir)
    config_data['sources']['slack']['enabled'] = False  # Disable Slack (needs real API)

    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    # Create output directory
    vault = tmp_path / "vault" / "Action Items"
    vault.mkdir(parents=True)
    (vault / "By Source").mkdir()
    (vault / "By Source" / "From Meetings").mkdir()
    (vault / "By Source" / "From Slack").mkdir()

    config_data['output']['path'] = str(tmp_path / "vault")

    config_file.write_text(yaml.dump(config_data))

    return str(persona_file), str(config_file)


class TestExtractor:
    def test_loads_enabled_sources(self, setup_configs):
        persona_path, config_path = setup_configs
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        # Should have meetings source loaded (Slack is disabled)
        assert len(extractor.sources) >= 1
        source_types = [type(s).__name__ for s in extractor.sources]
        assert 'LocalFilesSource' in source_types

    def test_skips_disabled_sources(self, setup_configs):
        persona_path, config_path = setup_configs
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        source_types = [type(s).__name__ for s in extractor.sources]
        assert 'SlackSource' not in source_types

    def test_loads_correct_output(self, setup_configs):
        persona_path, config_path = setup_configs
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        assert extractor.output is not None
        assert type(extractor.output).__name__ == 'ObsidianOutput'

    def test_plugin_loader_resolves_types(self, setup_configs):
        persona_path, config_path = setup_configs
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        # Verify the type->class mapping works
        assert 'local_files' in extractor.SOURCE_REGISTRY
        assert 'slack' in extractor.SOURCE_REGISTRY
        assert 'obsidian' in extractor.OUTPUT_REGISTRY
        assert 'markdown' in extractor.OUTPUT_REGISTRY
        assert 'csv' in extractor.OUTPUT_REGISTRY

    def test_extract_from_local_files(self, setup_configs):
        persona_path, config_path = setup_configs
        extractor = Extractor(persona_path=persona_path, config_path=config_path)
        raw_items = extractor.collect_raw_items()
        assert len(raw_items) >= 1
        assert any('review the spec' in item['content'].lower() for item in raw_items)
