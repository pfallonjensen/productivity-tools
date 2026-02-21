import pytest
from engine.config_loader import ConfigLoader


class TestConfigLoader:
    def test_loads_persona(self, sample_persona, tmp_path):
        """ConfigLoader reads persona.yaml and exposes identity"""
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert loader.user_name == "Test User"
        assert "TU" in loader.user_aliases
        assert loader.slack_user_id == "U12345TEST"

    def test_loads_projects(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert "main-product" in loader.projects
        assert loader.projects["main-product"]["extract_level"] == "all"

    def test_detect_project_by_keyword(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert loader.detect_project("We need to update the main product") == "main-product"
        assert loader.detect_project("The side project needs work") == "side-project"

    def test_detect_project_by_channel(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert loader.detect_project("random text", channel_id="C111111") == "main-product"

    def test_detect_project_unknown_returns_first(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        result = loader.detect_project("no keywords here")
        assert result is not None  # Returns first project as default

    def test_is_priority_contact(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert loader.is_priority_contact("boss.name") is True
        assert loader.is_priority_contact("random.person") is False

    def test_mentions_user(self, sample_persona, tmp_path):
        import yaml
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        loader = ConfigLoader(persona_path=str(persona_file))
        assert loader.mentions_user("Hey Test User, can you look at this?") is True
        assert loader.mentions_user("Hey TU, can you look at this?") is True
        assert loader.mentions_user("<@U12345TEST> please review") is True
        assert loader.mentions_user("This doesn't mention anyone relevant") is False

    def test_missing_persona_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ConfigLoader(persona_path=str(tmp_path / "nonexistent.yaml"))
