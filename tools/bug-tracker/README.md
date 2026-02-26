# Bug & Enhancement Tracker for Claude Code

A lightweight ticket system for tracking bugs and enhancements in any Claude Code project — covering both technical Claude infrastructure (skills, automations, hooks) and your own project domains.

Designed to work hand-in-hand with Claude Code: file a ticket mid-conversation, then resume it in any future session.

> **Works for any project folder, not just Obsidian.** Uses a `.claude/` directory and plain markdown files — it works wherever Claude Code works.

---

## What This Is

Most bug/enhancement trackers are built for software teams. This one is built for a solo knowledge worker using Claude Code. It handles two types of tickets:

- **Technical tickets** — Claude skills, automations, hooks, memory architecture. These follow a structured debugging/design workflow using Claude Code superpowers (optional).
- **Project tickets** — Personal and work projects. These use a lighter action-plan format.

Both types share the same filing format and live in the same folder, distinguished by their category prefix.

---

## Quick Start

**Option A — Interactive installer (recommended):**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/tools/bug-tracker/install.sh)
```

Run from your project root. The installer:
1. Creates `.claude/Bugs-to-Fix/` with templates
2. Optionally installs `/log-bug`, `/log-enh`, `/review-tickets` skills
3. Optionally adds the tracker snippet to your `CLAUDE.md`

**Option B — Let Claude set it up:**

1. Download this README and drop it anywhere in your project
2. Open Claude Code in your project directory
3. Say: *"Read [path/to/this/README.md] and set up the bug and enhancement tracker for my project. Use my actual folder structure to define the category prefixes."*

**Option C — Manual:**

1. Create `.claude/Bugs-to-Fix/` in your project root
2. Copy `BUG-TEMPLATE.md`, `ENH-TEMPLATE.md`, and the installed `README.md` from `templates/` into that folder
3. Optionally add the CLAUDE.md snippet below

---

## File Structure After Install

```
your-project/
├── CLAUDE.md                          ← Add tracker snippet here
└── .claude/
    ├── Bugs-to-Fix/
    │   ├── README.md                  ← Claude's operational reference
    │   ├── BUG-TEMPLATE.md
    │   ├── ENH-TEMPLATE.md
    │   └── ARCH-BUG-001-example.md   ← Actual tickets
    ├── learnings/
    │   └── LEARNINGS.jsonl            ← Append-only learnings log
    └── skills/
        ├── log-bug/skill.md
        ├── log-enh/skill.md
        └── review-tickets/skill.md
```

**Two layers of memory:**
- Tickets are ephemeral — they close when resolved
- Learnings are permanent — every resolved ticket appends a record of root cause, fix, and what to watch for. Future Claude sessions read this and skip rediscovering patterns you've already seen.

---

## CLAUDE.md Snippet

To enable automatic ticket filing, add this to your `CLAUDE.md`:

```markdown
## Bug & Enhancement Tracker

When a bug, error, or broken behavior comes up mid-conversation, offer to file a ticket:
> "Want me to file a bug ticket for this?"

When the user has an idea or improvement request, offer to file an ENH ticket:
> "Want me to file an enhancement for this?"

If yes, use the /log-bug or /log-enh skill. If skills are not installed, copy the
appropriate template from .claude/Bugs-to-Fix/, fill it in using the current session
context (session ID, timestamp, search terms), capture the user's words with minimal
editing, and save the file with the correct naming convention.
```

Without this snippet, you can still file tickets manually or by asking Claude explicitly — it just won't be offered automatically.

---

## Category Prefixes

The default technical prefixes work for any Claude Code project. Customize the project prefixes for your own domains.

### Technical (Claude Infrastructure)

| Prefix | What it covers |
|--------|---------------|
| `ARCH` | Project architecture — CLAUDE.md, context files, memory system |
| `SKILLS` | Claude skills — changes, templates, guide maintenance |
| `AUTO` | Automations — LaunchAgents, scripts, cron jobs |
| `HOOKS` | Hooks and notifications |
| `MEM` | Memory system — MEMORY.md, persistent context |

### Project (Customize These)

Add prefixes that match your project areas. Examples:

| Prefix | Example coverage |
|--------|-----------------|
| `WORK` | Work projects, deliverables, strategy |
| `PERSONAL` | Personal projects |
| `DIY` | Home repair and improvement |
| `GOALS` | Goals tracking |
| `WRITING` | Writing projects and content |

**To customize:** After installing, open Claude Code and say: *"Read .claude/Bugs-to-Fix/README.md and update the category prefixes to match my actual project folders."*

---

## How to File a Ticket

### Using skills (requires install)

```
/log-bug     — conversational intake, then writes ticket
/log-enh     — conversational intake, then writes ticket
/review-tickets — show all open tickets grouped by category
```

### Just telling Claude

```
"File a bug ticket for [describe the issue]"
"Log an ENH for [describe the idea]"
```

Claude will copy the appropriate template, fill in session context, and save the file.

---

## Naming Convention

```
{PREFIX}-{TYPE}-{NUM}-{short-slug}.md
```

**Examples:**
```
ARCH-ENH-001-claude-md-progressive-disclosure.md
SKILLS-BUG-001-missing-guide-entry.md
WORK-ENH-001-weekly-review-format.md
```

Numbering is per-prefix, not global.

---

## Session Context

Every ticket records the session it was filed in:

```markdown
**Session:** `~/.claude/projects/[project-path]/[SESSION-ID].jsonl`
**Logged at:** YYYY-MM-DD HH:MM
**Search terms:** "term1", "term2", "term3"
```

This lets you (or Claude) reopen the original conversation to read back the exact exchange. The search terms let you `grep` the JSONL quickly.

---

## Resuming a Ticket

In any future Claude Code session:

> "Read `.claude/Bugs-to-Fix/ARCH-ENH-001-example.md` and let's work on it."

Claude reads the ticket, loads context if needed, and resumes using the resolution workflow.

---

## Optional: Claude Code Superpowers

The resolution workflows reference [Claude Code Superpowers](https://github.com/anthropics/claude-code-superpowers) skills (`/superpowers:systematic-debugging`, `/superpowers:brainstorming`, `/superpowers:writing-plans`). These are optional — if you don't have them, delete those lines from the templates and work freeform, or substitute your own workflow steps.

---

## License

MIT
