# Action Item Extractor

**Extract action items from Slack, meetings, email, and more.**

A persona-driven extraction system that scans your communication channels, filters messages using configurable rules, and outputs structured action items. You define *who you are*, *what you own*, and *what matters* -- the engine handles the rest.

Works standalone, as an automated scheduled job, or as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill.

---

## Quick Start (5 minutes)

```bash
# 1. Clone and enter the repo
git clone https://github.com/pfallonjensen/action-item-extractor.git
cd action-item-extractor

# 2. Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create your persona config (who you are, what matters)
cp persona.example.yaml persona.yaml
# Edit persona.yaml with your identity, projects, themes, and contacts

# 4. Create your runtime config (sources, output, credentials)
cp config.example.yaml config.yaml
# Edit config.yaml with your API tokens, source paths, and output settings

# 5. Run the extraction pipeline
#    Option A: Two-step pipeline with AI triage (recommended — requires Claude Code)
./run-extract-tasks.sh

#    Option B: Keyword-only mode (no AI, no Claude Code needed)
python3 collect.py /tmp/action-item-candidates
```

> **New to this?** See the [Beginner Setup Guide](BEGINNER-SETUP-GUIDE.md) for step-by-step instructions with screenshots.

---

## Architecture

The system supports two modes. Choose the one that fits your setup:

### Two-Step Pipeline (Recommended)

Python handles data collection. Claude Code handles reasoning. This prevents context overflow on heavy days and catches implied asks that keyword matching misses.

```
Step 1: Python (collect.py)              Step 2: Claude Code (triage)
┌─────────┐                              ┌──────────────────────────┐
│  Slack   │──┐                          │ Reads candidates JSON:   │
├─────────┤  │  ┌───────────────────┐    │ - Keep/skip + reasoning  │
│ Meetings │──┼─▶│ Collect + noise   │───▶│ - Implied asks & context │
├─────────┤  │  │ filter → JSON     │    │ - Carry-forward logic    │
│  Jira   │──┤  └───────────────────┘    │ - Writes to vault/output │
├─────────┤  │                           └──────────────────────────┘
│ Gmail*  │──┘                           * Gmail fetched via MCP
```

**Requires:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed. Uses your existing subscription (Teams/Max/Pro) -- no extra API cost.

**Run it:** `./run-extract-tasks.sh`

### Keyword-Only Mode

Python handles everything. No Claude Code required. Uses persona rules (themes, projects, mentions, priority contacts) for filtering.

```
┌─────────┐    ┌───────────────────┐    ┌──────────────┐
│ Sources  │───▶│ ExtractionEngine  │───▶│    Output     │
│          │    │ + ReplyDetector   │    │              │
│          │    │ + TicketParser    │    │ Obsidian/MD/ │
│          │    │ + Deduplicator    │    │ CSV          │
└──────────┘    └───────────────────┘    └──────────────┘
```

**Run it:** `python3 collect.py /tmp/action-item-candidates`

### Pipeline stages (both modes):

1. **Collect** -- Each enabled source plugin fetches recent messages/content
2. **Noise Filter** -- Remove definitive noise (bots, skip keywords, awareness-only projects)
3. **AI Triage** (two-step mode only) -- Claude applies semantic reasoning: implied asks, contextual blockers, inferred urgency, two-way workflow detection
4. **Carry Forward** (two-step mode only) -- Incomplete items from previous days roll into today's list
5. **Save** -- Output plugin writes tasks in your preferred format

---

## Persona Configuration

The persona file (`persona.yaml`) is the core of the system. It defines your extraction "form" -- a reusable profile that controls what gets extracted and what gets skipped.

### Identity

Who you are. Messages mentioning your name, aliases, or Slack ID are always extracted.

```yaml
identity:
  name: "Your Name"
  aliases: ["First", "Initials", "username"]
  slack_user_id: "UXXXXXXXXXX"
  role: "Your Role Title"
```

### Projects

What you own. Each project has an **extract level** that controls extraction aggressiveness:

| Extract Level | Behavior | Use When |
|--------------|----------|----------|
| `all` | Extract any theme match | You own this project day-to-day |
| `strategic_only` | Extract only `critical` and `high` priority themes | Someone else runs day-to-day; you need strategic visibility |
| `awareness_only` | Flag but don't create tasks | You want to know about it, but it's not your problem |

```yaml
projects:
  my-product:
    name: "My Product"
    my_role: "I'm the PM and product owner"
    extract_level: all
    detect_keywords: ["my product", "MP"]
    channels: ["C04CHANNEL1", "C04CHANNEL2"]

  other-initiative:
    name: "Other Initiative"
    my_role: "Executive oversight only"
    extract_level: strategic_only
    detect_keywords: ["other initiative"]
    channels: []
```

Projects are detected by Slack channel ID (highest confidence) or keyword match in message text.

### Priority Contacts

People whose messages are always extracted, regardless of theme or project.

```yaml
priority_contacts:
  - username: "ceo.name"
    reason: "CEO - always extract"
  - username: "key.stakeholder"
    reason: "Key stakeholder"
```

### Themes

Keyword-based topic matching. Each theme has a **priority** that determines whether it qualifies for `strategic_only` extraction.

```yaml
themes:
  blocking:
    priority: critical     # Extracted for ALL project levels
    description: "Team blocked, needs your input"
    keywords:
      - "blocked"
      - "can't proceed"
      - "need decision"

  coordination:
    priority: medium       # Extracted for 'all' projects, skipped for 'strategic_only'
    keywords:
      - "sync"
      - "align"
      - "handoff"
```

Priority hierarchy: `critical` > `high` > `medium` > `low`

Themes with `critical` or `high` priority are extracted for both `all` and `strategic_only` projects. Themes with `medium` or `low` priority are only extracted for `all` projects.

### Skip Keywords

Messages containing these keywords are never extracted (overridden by direct mentions and priority contacts).

```yaml
skip_keywords:
  - "typo"
  - "minor bug"
  - "formatting"
```

### Ticket Detection

Automatically finds ticket references (e.g., `PROJ-123`) and detects assignees.

```yaml
ticket_detection:
  enabled: true
  pattern: '[A-Z]{2,5}-\d{1,5}'  # Jira/Linear style
  # pattern: '#\d+'              # GitHub issues
  # pattern: 'T\d{7,}'          # Phabricator
```

The ticket parser also detects assignment patterns like:
- "Alice will pick up PROJ-123"
- "PROJ-456 assigned to Bob"
- "Charlie is taking PROJ-789"

---

## Sources

Source plugins fetch raw content from your communication channels. Enable them in `config.yaml`.

| Source | Type | Config Key | What It Scans |
|--------|------|-----------|---------------|
| **Slack** | `slack` | `token`, `workspace` | DMs, group DMs, and configured channels |
| **Local Files** | `local_files` | `path`, `file_patterns` | Meeting transcripts, notes in a directory |
| **Jira** | `jira` | `cloud_id`, `token`, `email` | Recent issues and comments |
| **Confluence** | `confluence` | `cloud_id`, `token` | Recently updated pages |
| **Email** | `email` | `provider`, `credentials_path` | Gmail or other email providers |

### Slack Setup

1. Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Add OAuth scopes: `channels:history`, `im:history`, `mpim:history`, `users:read`
3. Install to workspace and copy the User OAuth Token (`xoxp-...`)
4. Add to `config.yaml`:

```yaml
sources:
  slack:
    enabled: true
    type: slack
    token: "xoxp-YOUR-TOKEN"
    workspace: "your-workspace"   # The subdomain from your-workspace.slack.com
    lookback_hours: 24
```

### Local Files (Meeting Transcripts) Setup

Point at a directory containing transcript files. The source scans for files modified within the lookback period.

```yaml
sources:
  meetings:
    enabled: true
    type: local_files
    path: "/path/to/meeting/transcripts"
    file_patterns: ["*.txt", "*.md"]
    lookback_hours: 48
```

### Jira Setup

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create an API token
3. Find your Cloud ID: go to `YOUR-SITE.atlassian.net/_edge/tenant_info` and copy the `cloudId` value

```yaml
sources:
  jira:
    enabled: true
    type: jira
    cloud_id: "YOUR_CLOUD_ID"
    site: "YOUR_SITE"              # The subdomain from YOUR_SITE.atlassian.net
    token: "YOUR_API_TOKEN"
    email: "your.email@company.com"
    lookback_days: 7
    projects: ["PROJ", "TEAM"]
```

### Confluence Setup

```yaml
sources:
  confluence:
    enabled: true
    type: confluence
    cloud_id: "YOUR_CLOUD_ID"
    token: "YOUR_API_TOKEN"
    lookback_days: 7
```

### Email Setup

```yaml
sources:
  email:
    enabled: true
    type: email
    provider: gmail
    credentials_path: "/path/to/credentials.json"
    lookback_hours: 24
```

---

## Outputs

Output plugins control where extracted tasks are saved.

| Output | Type | Description |
|--------|------|-------------|
| **Obsidian** | `obsidian` | Rich markdown with urgency grouping, priority emojis, carry-forward, source-specific files |
| **Markdown** | `markdown` | Simple markdown files, no Obsidian-specific syntax |
| **CSV** | `csv` | Spreadsheet-ready CSV for import into other tools |

### Obsidian Output

The most full-featured output. Creates daily action item files with:
- Manual priorities section (preserved across runs)
- Urgency groups: Today, Past Due, Urgent This Week, This Week, Later
- Priority emojis and receipts tables (who, where, when, link)
- Source-specific subdirectory files (By Source/From Slack, From Meetings, etc.)
- Carry-forward for incomplete tasks
- Fuzzy deduplication against existing tasks

```yaml
output:
  type: obsidian
  path: "/path/to/your/vault"
  action_items_path: "Action Items"
  preserve_manual_priorities: true
  carry_forward_incomplete: true
  past_due_tracking: true
```

### Markdown Output

```yaml
output:
  type: markdown
  path: "/path/to/output/directory"
```

### CSV Output

```yaml
output:
  type: csv
  path: "/path/to/output/directory"
```

CSV columns: `title`, `priority`, `due_date`, `requestor`, `project`, `context`, `source_type`, `source_url`, `confidence`

---

## AI Processing

The `triage_mode` setting controls how AI reasoning is applied:

| Mode | How It Works | Cost | Requires |
|------|-------------|------|----------|
| `claude_code` | Claude Code CLI runs semantic triage via `run-extract-tasks.sh` | $0 extra (uses your subscription) | Claude Code installed, Teams/Max/Pro plan |
| `api` | Anthropic API enriches tasks with titles, priorities, due dates | Pay-per-use (~$0.01-0.05/run) | API key |
| `none` | Keyword-only filtering, no AI | Free | Nothing |

```yaml
ai:
  triage_mode: "claude_code"   # claude_code | api | none

  # Only needed if triage_mode: "api"
  # api_key: "YOUR_ANTHROPIC_API_KEY"
  # model: "claude-sonnet-4-5-20250929"
  confidence_threshold: 0.7
```

**`claude_code` mode** (recommended) catches things keyword matching misses: implied asks, contextual blockers, inferred urgency, and two-way workflow detection. It uses the triage prompt at `prompts/triage.md` and writes output directly to your vault.

---

## Custom Rules

For logic that goes beyond keyword matching, create a `custom_rules.py` in the project root.

```bash
cp custom_rules.example.py custom_rules.py
```

### Override Extraction Decisions

```python
def should_extract(text, project, themes, persona_config):
    """Return (bool, reason) to override, or None to use default logic."""

    # Always extract messages containing "URGENT"
    if "URGENT" in text.upper():
        return (True, "Custom rule: URGENT keyword")

    # Never extract from a specific bot
    if "@automation-bot" in text:
        return (False, "Custom rule: skip automation bot")

    # Fall through to default engine logic
    return None
```

### Post-Process Extracted Tasks

```python
def custom_post_process(tasks, persona_config):
    """Modify tasks after extraction -- re-prioritize, merge, filter."""

    for task in tasks:
        if task.get('project') == 'critical-project':
            task['priority'] = 'high'
    return tasks
```

Custom rules are loaded automatically if `custom_rules.py` exists. The file is `.gitignore`d by default since rules often contain organization-specific logic.

---

## Automation

### Run Scripts

There are two run scripts depending on your mode:

| Script | Mode | What It Does |
|--------|------|-------------|
| `run-extract-tasks.sh` | Two-step (recommended) | Python collection → Claude Code triage. Handles retries, timeouts, auth checks. |
| `automation/run.sh` | Keyword-only | Python-only pipeline. No Claude Code needed. |

```bash
# Two-step pipeline (recommended)
./run-extract-tasks.sh
./run-extract-tasks.sh --persona /path/to/persona.yaml --config /path/to/config.yaml

# Keyword-only
./automation/run.sh
./automation/run.sh -p /path/to/persona.yaml -c /path/to/config.yaml
```

### Environment Variables

API tokens can be stored in a `.env` file (sourced automatically by both run scripts):

```bash
# .env (create in project root — already gitignored)
export SLACK_TOKEN="xoxp-YOUR-TOKEN"
export JIRA_API_TOKEN="YOUR-JIRA-TOKEN"
```

Then reference them in `config.yaml` with `${SLACK_TOKEN}` and `${JIRA_API_TOKEN}`. The config loader expands environment variables automatically.

### macOS LaunchAgent

Run extraction on a schedule (e.g., 6am, 11am, 3pm, 6pm):

```bash
# 1. Copy and edit the template
cp automation/launchagent.example.plist ~/Library/LaunchAgents/com.action-item-extractor.plist

# 2. Edit the plist: replace /PATH/TO/ with your actual paths
#    - ProgramArguments: path to run-extract-tasks.sh (or automation/run.sh)
#    - StandardOutPath: path to your log file
#    - WorkingDirectory: path to the project root

# 3. Load the agent
launchctl load ~/Library/LaunchAgents/com.action-item-extractor.plist

# 4. Verify it's loaded
launchctl list | grep action-item
```

### Cron (Linux/macOS)

```bash
# Add to crontab (crontab -e):
0 6,11,15,18 * * * /path/to/action-item-extractor/run-extract-tasks.sh >> /path/to/extract-tasks.log 2>&1
```

---

## Claude Code Integration

Use the extractor as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill or slash command.

### As a Skill

Copy `claude-code/skills/extract-tasks/` into your project's `.claude/skills/` directory:

```bash
cp -r claude-code/skills/extract-tasks /path/to/your/project/.claude/skills/
```

Then invoke in Claude Code:
```
/extract-tasks
```

### As a Command

Copy `claude-code/commands/extract-tasks.md` into your project's `.claude/commands/` directory:

```bash
cp claude-code/commands/extract-tasks.md /path/to/your/project/.claude/commands/
```

Both the skill and command run the same extraction pipeline using your `persona.yaml` and `config.yaml`.

---

## Example Personas

The `examples/` directory contains complete persona files for different roles:

| File | Role | Description |
|------|------|-------------|
| `vp-product-persona.yaml` | VP of Product | Owns one product, executive oversight on another, awareness-only on a third |
| `engineering-manager-persona.yaml` | Engineering Manager | Team-focused with sprint, incident, and hiring themes |
| `founder-ceo-persona.yaml` | Founder/CEO | Broad visibility across all functions with investor and fundraising themes |

Use these as starting points:

```bash
cp examples/vp-product-persona.yaml persona.yaml
# Edit to match your identity, projects, and themes
```

---

## Project Structure

```
action-item-extractor/
  collect.py              # Step 1 entry point — data collection + noise filter
  run-extract-tasks.sh    # Two-step runner (Python → Claude Code triage)
  engine/
    extractor.py          # Main orchestrator (plugin loader, pipeline runner)
    extraction_engine.py  # Rule-based filtering (themes, projects, mentions)
    config_loader.py      # Loads persona.yaml + config.yaml (expands env vars)
    reply_detection.py    # Smart reply detection (substantive vs. deferred)
    ticket_parser.py      # Ticket reference finder with assignee detection
    dedup.py              # Fingerprint + fuzzy deduplication
    ai_processor.py       # Claude API integration for task enrichment
    custom_rules.py       # Custom rules loader
  sources/
    base_source.py        # Abstract base class for source plugins
    slack_source.py       # Slack DMs and channels
    local_files_source.py # Local files (meeting transcripts)
    jira_source.py        # Jira issues and comments
    confluence_source.py  # Confluence pages
    email_source.py       # Email (Gmail, etc.)
  outputs/
    base_output.py        # Abstract base class for output plugins
    obsidian_output.py    # Obsidian vault output with smart management
    markdown_output.py    # Simple markdown files
    csv_output.py         # CSV for spreadsheet import
  prompts/
    triage.md             # AI triage prompt (used by Step 2 of two-step pipeline)
  automation/
    run.sh                # Keyword-only shell runner (no Claude Code)
    launchagent.example.plist  # macOS LaunchAgent template
    cron.example          # Cron schedule template
  claude-code/
    skills/extract-tasks/ # Claude Code skill definition
    commands/             # Claude Code slash command
  examples/               # Example persona configs for different roles
  tests/                  # Test suite
  persona.example.yaml    # Persona template
  config.example.yaml     # Config template
  custom_rules.example.py # Custom rules template
```

---

## Contributing

### Adding a New Source Plugin

1. Create `sources/my_source.py` extending `BaseSource`:

```python
from sources.base_source import BaseSource
from typing import List, Dict

class MySource(BaseSource):
    def extract(self) -> List[Dict]:
        """Return list of items with keys: content, author, timestamp, url, metadata"""
        items = []
        # ... fetch from your source ...
        items.append({
            'content': 'message text',
            'author': 'sender_username',
            'timestamp': datetime_object,
            'url': 'https://link-to-source',
            'metadata': {
                'source_type': 'my_source',
                # ... additional metadata ...
            }
        })
        return items

    def is_available(self) -> bool:
        """Return True if the source is configured and reachable."""
        return bool(self.source_config.get('api_key'))
```

2. Register it in `engine/extractor.py`:

```python
SOURCE_REGISTRY = {
    # ... existing sources ...
    'my_source': ('sources.my_source', 'MySource'),
}
```

3. Add configuration to `config.yaml`:

```yaml
sources:
  my_source:
    enabled: true
    type: my_source
    api_key: "YOUR_KEY"
```

### Adding a New Output Plugin

1. Create `outputs/my_output.py` extending `BaseOutput`:

```python
from outputs.base_output import BaseOutput
from typing import List, Dict

class MyOutput(BaseOutput):
    def save_tasks(self, tasks: List[Dict]) -> None:
        """Save extracted tasks. Each task has: title, priority, due_date,
        requestor, context, project, source_url, source_type, confidence."""
        pass

    def update_dashboard(self) -> None:
        """Update any summary view (optional)."""
        pass
```

2. Register it in `engine/extractor.py`:

```python
OUTPUT_REGISTRY = {
    # ... existing outputs ...
    'my_output': ('outputs.my_output', 'MyOutput'),
}
```

### Running Tests

```bash
pip install -r requirements-dev.txt
pytest
pytest --cov=engine --cov=sources --cov=outputs
```

---

## License

MIT -- see [LICENSE](LICENSE) for details.
