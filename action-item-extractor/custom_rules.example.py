"""
Custom Rules Template — Optional advanced logic for action item extraction.

Copy this file to `custom_rules.py` and modify to add your own extraction logic.
The engine calls these functions if custom_rules.py exists in the project root.

Functions:
- should_extract(): Override the extraction decision for any message
- custom_post_process(): Modify tasks after extraction (re-prioritize, merge, etc.)
"""


def should_extract(text, project, themes, persona_config):
    """
    Override extraction decision for a message.

    Args:
        text: The message text
        project: Detected project key (from persona.yaml projects)
        themes: List of matched theme names
        persona_config: Full persona.yaml dict

    Returns:
        tuple[bool, str]: (should_extract, reason) to override
        None: Fall through to default engine logic

    Examples:
        # Always extract messages containing "URGENT"
        if "URGENT" in text.upper():
            return (True, "Custom rule: URGENT keyword")

        # Never extract from a specific bot
        if "@automation-bot" in text:
            return (False, "Custom rule: skip automation bot")

        # Fall through to default logic for everything else
        return None
    """
    return None  # Default: use engine logic


def custom_post_process(tasks, persona_config):
    """
    Modify tasks after extraction — re-prioritize, merge, filter, etc.

    Args:
        tasks: List of extracted task dicts
        persona_config: Full persona.yaml dict

    Returns:
        Modified list of task dicts

    Examples:
        # Bump priority for tasks from a specific project
        for task in tasks:
            if task.get('project') == 'critical-project':
                task['priority'] = 'high'
        return tasks
    """
    return tasks
