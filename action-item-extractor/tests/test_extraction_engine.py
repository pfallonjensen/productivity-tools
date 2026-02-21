import pytest
from engine.config_loader import ConfigLoader
from engine.extraction_engine import ExtractionEngine
import yaml


def _make_engine(sample_persona, tmp_path):
    persona_file = tmp_path / "persona.yaml"
    persona_file.write_text(yaml.dump(sample_persona))
    loader = ConfigLoader(persona_path=str(persona_file))
    return ExtractionEngine(loader)


class TestExtractionEngine:
    def test_always_extract_when_mentioned(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="Hey Test User, can you review this?",
            author_username="random.person",
            channel_id=None
        )
        assert result.extract is True
        assert "mentioned" in result.reason.lower()

    def test_always_extract_from_priority_contact(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="Can someone look at this bug?",
            author_username="boss.name",
            channel_id=None
        )
        assert result.extract is True
        assert "priority" in result.reason.lower()

    def test_skip_when_skip_keywords(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="Fixed a typo in the docs",
            author_username="random.person",
            channel_id=None
        )
        assert result.extract is False

    def test_extract_critical_theme_for_all_level_project(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="The main product team is blocked on the spec",
            author_username="random.person",
            channel_id="C111111"
        )
        assert result.extract is True

    def test_extract_high_theme_for_all_level_project(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="We need to update the main product roadmap",
            author_username="random.person",
            channel_id="C111111"
        )
        assert result.extract is True

    def test_skip_low_theme_for_strategic_only_project(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="Side project fyi heads up",
            author_username="random.person",
            channel_id="C222222"
        )
        assert result.extract is False

    def test_extract_critical_theme_for_strategic_only_project(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="The side project team is blocked",
            author_username="random.person",
            channel_id="C222222"
        )
        assert result.extract is True

    def test_no_theme_match_no_mention_skips(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="The weather is nice today",
            author_username="random.person",
            channel_id=None
        )
        assert result.extract is False

    def test_matched_themes_returned(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="We're blocked and need a roadmap decision for the main product",
            author_username="random.person",
            channel_id="C111111"
        )
        assert result.extract is True
        assert "blocking" in result.matched_themes or "strategic" in result.matched_themes

    def test_project_detected_in_result(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.should_extract(
            text="Main product needs attention",
            author_username="boss.name",
            channel_id=None
        )
        assert result.project == "main-product"
