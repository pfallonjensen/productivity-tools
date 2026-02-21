---
name: extract-tasks
description: Extract action items from configured sources (Slack, meetings, email, Jira) using your persona config
---

# Extract Tasks Skill

You are a specialized agent that extracts action items from configured communication sources and saves them to your preferred output format.

## Configuration

This skill reads two config files:
- **persona.yaml** — Your identity, projects, themes, contacts, and rules
- **config.yaml** — Source credentials, output type, AI settings, schedule

## How It Works

1. **Load config** — Reads persona.yaml and config.yaml
2. **Scan sources** — Reads from all enabled sources (Slack, meetings, Jira, etc.)
3. **Apply rules** — Uses your persona config to decide what to extract:
   - Always extract: messages that mention you or come from priority contacts
   - Theme matching: matches keywords to your defined themes
   - Project filtering: applies extract_level (all / strategic_only / awareness_only)
   - Smart reply detection: skips threads where you already gave a substantive answer
4. **Deduplicate** — Removes duplicates using fuzzy title matching
5. **AI enrichment** — Uses Claude to extract structured action items with titles, priorities, due dates
6. **Save** — Outputs to your configured format (Obsidian, markdown, or CSV)

## Running

### Via Python directly:

```bash
cd /path/to/action-item-extractor
python3 -c "
from engine.extractor import Extractor
extractor = Extractor(persona_path='persona.yaml', config_path='config.yaml')
result = extractor.run()
print(f'Done: {result[\"saved\"]} tasks saved')
"
```

### Via automation script:

```bash
./automation/run.sh
```

### Via Claude Code:

```
/extract-tasks
```

## Customization

### Custom extraction rules (optional):

Copy `custom_rules.example.py` to `custom_rules.py` and add your own logic:

```python
def should_extract(text, project, themes, persona_config):
    if "URGENT" in text.upper():
        return (True, "Custom: URGENT keyword")
    return None  # Fall through to default logic
```

### Adding new sources or outputs:

1. Create a new class extending `BaseSource` or `BaseOutput`
2. Add it to the registry in `engine/extractor.py`
3. Add the type to your `config.yaml`

## Output Format

Tasks are saved with:
- Title and priority emoji (high, medium, low)
- Due date and project tag
- Receipts table (who requested, from where, when, link)
- Action context

## Troubleshooting

- **No tasks extracted?** Check that your persona.yaml themes match the keywords in your messages
- **Too many tasks?** Tighten extract_level to `strategic_only` for less critical projects
- **Missing source?** Verify the source is `enabled: true` in config.yaml and credentials are correct
