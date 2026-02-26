---
name: review-tickets
description: Show open bugs and enhancements from .claude/Bugs-to-Fix/ grouped by category
user_invocable: true
---

# Review Tickets

Display open bugs and enhancements from the tracker, grouped by category prefix.

## Usage

- `/review-tickets` — all OPEN and IN PROGRESS tickets
- `/review-tickets [PREFIX]` — filter by category (e.g., `/review-tickets ARCH`)
- `/review-tickets all` — everything including DONE and WONT FIX

## Steps

### Step 1: Find the project root and list ticket files

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
ls "$PROJECT_ROOT/.claude/Bugs-to-Fix/"*.md 2>/dev/null | grep -v "README\|TEMPLATE"
```

If no files found (only README/templates exist), say: "No tickets filed yet. Use `/log-bug` or `/log-enh` to file one."

### Step 2: Extract metadata from each file

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
for f in "$PROJECT_ROOT/.claude/Bugs-to-Fix/"*.md; do
  name=$(basename "$f" .md)
  [[ "$name" == *"TEMPLATE"* || "$name" == "README" ]] && continue
  status=$(grep -m1 "^\*\*Status:\*\*" "$f" | sed 's/.*\*\*Status:\*\* *//' | tr -d '\r')
  priority=$(grep -m1 "^\*\*Priority:\*\*\|\*\*Severity:\*\*" "$f" | sed 's/.*\*\*\(Priority\|Severity\):\*\* *//' | tr -d '\r')
  title=$(grep -m1 "^# " "$f" | sed 's/^# //')
  echo "$name|||$status|||$priority|||$title"
done
```

### Step 3: Apply filters

- Default (no args): show only `OPEN` and `IN PROGRESS`
- `[PREFIX]` arg: also filter to only that prefix (e.g., `ARCH-*`)
- `all` arg: show all statuses

### Step 4: Format and display

Group tickets by category prefix. Within each group, show IN PROGRESS first, then OPEN, then (if `all`) BLOCKED / DONE / WONT FIX.

Format:

```
## Open Tickets — 5 total (2 bugs, 3 enhancements)

### ARCH
🔴 IN PROGRESS  ARCH-ENH-001  Claude.md progressive disclosure
⚪ OPEN         ARCH-BUG-001  Memory file growing too large

### SKILLS
⚪ OPEN         SKILLS-ENH-001  Add version field to skill frontmatter

### WORK
⚪ OPEN         WORK-ENH-001  Weekly review format
⚪ OPEN         WORK-BUG-001  Missing context in handoff doc

[No open tickets for: AUTO, HOOKS, MEM, PERSONAL, DIY, GOALS, WRITING]
```

Priority/Severity indicators:
- 🔴 HIGH (or IN PROGRESS)
- 🟡 MEDIUM
- ⚪ LOW or unset
- ✅ DONE

### Step 5: Offer next action

After displaying, say:
> "To work on a ticket: 'Read `.claude/Bugs-to-Fix/[filename]` and let's work on it.'"
