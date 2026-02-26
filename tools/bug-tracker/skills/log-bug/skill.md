---
name: log-bug
description: Conversational bug intake — ask questions and file a structured ticket to .claude/Bugs-to-Fix/
user_invocable: true
---

# Log Bug

File a bug ticket via conversation. Gather context from the user, then write a complete ticket file.

## Usage

- `/log-bug` — start intake conversationally
- `/log-bug [description]` — skip the first question if description is already provided

## Steps

### Step 1: Gather bug info

If the user hasn't already described the bug, ask:

1. **What's broken?** (capture their exact words)
2. **Category prefix?** — suggest based on what they described. If you're not sure, read `.claude/Bugs-to-Fix/README.md` for the prefix table.
3. **Severity?** HIGH / MEDIUM / LOW — suggest based on impact. High = broken workflow, data loss, or blocking. Medium = degraded but workaround exists. Low = cosmetic or edge case.

Only ask what you don't already know from context. Don't ask for a date — use today's date.

### Step 2: Find the project root and next ticket number

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
TRACKER_DIR="$PROJECT_ROOT/.claude/Bugs-to-Fix"
ls "$TRACKER_DIR"/{PREFIX}-BUG-*.md 2>/dev/null | sort | tail -1
```

Replace `{PREFIX}` with the actual prefix. Increment the highest number by 1, starting at 001 if none exist.

### Step 3: Write the ticket

Copy BUG-TEMPLATE.md, fill in all fields, and save as:

```
$TRACKER_DIR/{PREFIX}-BUG-{NUM}-{short-slug}.md
```

**Fill in the Context block using this session:**
- **Session path**: This session's JSONL file — Claude knows its own session ID. Find it at `~/.claude/projects/[encoded-project-path]/[SESSION-ID].jsonl`
- **Logged at**: Current date and time
- **Search terms**: 2-4 terms that would locate this exchange when grepped in the session file

### Step 4: Confirm

Tell the user the filename that was created. Offer: "Want to start working on it now, or file it for later?"
