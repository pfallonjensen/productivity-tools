import pytest
import yaml
import sys
from pathlib import Path
from engine.config_loader import ConfigLoader
from engine.extraction_engine import ExtractionEngine
from engine.custom_rules import load_custom_rules


class TestCustomRules:
    def test_loads_custom_rules_module(self, tmp_path, sample_persona):
        # Create custom_rules.py
        rules_file = tmp_path / "custom_rules.py"
        rules_file.write_text('''
def should_extract(text, project, themes, persona_config):
    """Custom override."""
    if "URGENT" in text.upper():
        return (True, "Custom rule: URGENT keyword found")
    return None  # Fall through to default logic
''')

        module = load_custom_rules(str(rules_file))
        assert module is not None
        assert hasattr(module, 'should_extract')

    def test_custom_rules_override_engine(self, tmp_path, sample_persona):
        # Create persona file
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        # Create custom rules that always extract "URGENT"
        rules_file = tmp_path / "custom_rules.py"
        rules_file.write_text('''
def should_extract(text, project, themes, persona_config):
    if "URGENT" in text.upper():
        return (True, "Custom: URGENT keyword")
    return None
''')

        loader = ConfigLoader(persona_path=str(persona_file))
        custom = load_custom_rules(str(rules_file))
        engine = ExtractionEngine(loader, custom_rules=custom)

        # This text has no theme match and no mention, but has URGENT
        result = engine.should_extract(
            text="URGENT: The cafeteria menu changed",
            author_username="random.person"
        )
        assert result.extract is True
        assert "Custom" in result.reason

    def test_custom_rules_fall_through(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))

        rules_file = tmp_path / "custom_rules.py"
        rules_file.write_text('''
def should_extract(text, project, themes, persona_config):
    return None  # Always fall through
''')

        loader = ConfigLoader(persona_path=str(persona_file))
        custom = load_custom_rules(str(rules_file))
        engine = ExtractionEngine(loader, custom_rules=custom)

        # Falls through to normal engine logic — should skip (no theme, no mention)
        result = engine.should_extract(
            text="The weather is nice",
            author_username="random.person"
        )
        assert result.extract is False

    def test_missing_custom_rules_returns_none(self, tmp_path):
        module = load_custom_rules(str(tmp_path / "nonexistent.py"))
        assert module is None

    def test_custom_post_process(self, tmp_path):
        rules_file = tmp_path / "custom_rules.py"
        rules_file.write_text('''
def should_extract(text, project, themes, persona_config):
    return None

def custom_post_process(tasks, persona_config):
    """Double the priority of all tasks."""
    for task in tasks:
        if task.get("priority") == "medium":
            task["priority"] = "high"
    return tasks
''')

        module = load_custom_rules(str(rules_file))
        assert hasattr(module, 'custom_post_process')

        tasks = [{"title": "Test", "priority": "medium"}]
        result = module.custom_post_process(tasks, {})
        assert result[0]["priority"] == "high"
