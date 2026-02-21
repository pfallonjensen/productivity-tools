"""
Custom rules loader — dynamically loads user's custom_rules.py if it exists.
"""
import importlib.util
import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger('custom_rules')


def load_custom_rules(path: str) -> Optional[object]:
    """
    Load custom rules module from a Python file.

    The module can optionally define:
    - should_extract(text, project, themes, persona_config) -> tuple[bool, str] | None
    - custom_post_process(tasks, persona_config) -> list

    Returns the loaded module, or None if file doesn't exist.
    """
    p = Path(path)
    if not p.exists():
        logger.debug(f"No custom rules at {path}")
        return None

    try:
        spec = importlib.util.spec_from_file_location("custom_rules", str(p))
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create module spec from {path}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info(f"Loaded custom rules from {path}")
        return module

    except Exception as e:
        logger.error(f"Error loading custom rules from {path}: {e}")
        return None
