# Bug & Enhancement Tracker

A lightweight ticket system for tracking bugs and enhancements in any project — covering both technical Claude Code infrastructure (skills, automations, hooks) and your own project domains.

Designed to work hand-in-hand with Claude Code: file a ticket mid-conversation, then resume it in any future session.

---

## File Structure

```
.claude/
├── Bugs-to-Fix/
│   ├── README.md               ← You are here
│   ├── BUG-TEMPLATE.md         ← Copy this to file a bug
│   ├── ENH-TEMPLATE.md         ← Copy this to file an enhancement
│   └── {PREFIX}-{TYPE}-{NUM}-{slug}.md   ← Actual tickets
└── learnings/
    └── LEARNINGS.jsonl         ← Append-only log: root causes, fixes, watch-fors
```

**Two layers of memory:**
- **Tickets** (`.claude/Bugs-to-Fix/`) — active work items, resolved when done
- **Learnings** (`.claude/learnings/LEARNINGS.jsonl`) — permanent record of what was learned; survives ticket closure; builds judgment over time

**Examples:**
```
ARCH-ENH-001-claude-md-progressive-disclosure.md
SKILLS-BUG-001-missing-guide-entry.md
AUTO-BUG-001-backup-launchagent-failure.md
WORK-ENH-001-weekly-review-format.md
DIY-BUG-001-hvac-inspection-followup.md
```

---

## Naming Convention

```
{PREFIX}-{TYPE}-{NUM}-{short-slug}.md
```

| Part | Values | Notes |
|------|--------|-------|
| `PREFIX` | See category table below | Identifies the domain |
| `TYPE` | `BUG` or `ENH` | Bug = something broken. ENH = something to improve or build. |
| `NUM` | `001`, `002`, `003`... | Each prefix has its own independent counter |
| `slug` | lowercase-hyphenated | 3-6 words describing the issue |

**Numbering is per-prefix, not global.** `ARCH-ENH-001` and `SKILLS-ENH-001` are different tickets.

---

## Category Prefixes

> **Customize this table.** The technical prefixes below are built for Claude Code infrastructure and can stay as-is. Replace the project prefixes with your own domains.

### Technical (Claude Infrastructure)

| Prefix | What it covers |
|--------|---------------|
| `ARCH` | Project architecture — CLAUDE.md, context files, memory system |
| `SKILLS` | Claude skills — changes, templates, guide maintenance |
| `AUTO` | Automations — LaunchAgents, scripts, cron jobs |
| `HOOKS` | Hooks and notifications |
| `MEM` | Memory system — MEMORY.md, persistent context |

### Project (Customize These)

| Prefix | Example coverage |
|--------|-----------------|
| `WORK` | Work projects, strategies, deliverables |
| `PERSONAL` | Personal projects |
| `DIY` | Home repair and improvement |
| `GOALS` | Goals tracking |
| `WRITING` | Writing projects and content |

> **To customize:** Open Claude Code and say: *"Read .claude/Bugs-to-Fix/README.md and update the category prefixes to match my actual project folders."* Claude will read your folder structure and propose a customized prefix table.

---

## Status Values

| Status | Meaning |
|--------|---------|
| `OPEN` | Filed, not yet started |
| `IN PROGRESS` | Actively being worked |
| `BLOCKED` | Waiting on something external |
| `✅ DONE` | Resolved |
| `WONT FIX` | Closed without action |

---

## How to File a Ticket

### During a Claude Code session (recommended)

Tell Claude:

> "File a bug ticket for [describe the issue]" or "File an ENH for [describe the idea]"

Claude will:
1. Copy the appropriate template
2. Fill in the session context automatically (session ID, timestamp, search terms)
3. Capture your words with minimal editing
4. Name and save the file

### Manually

1. Copy `BUG-TEMPLATE.md` or `ENH-TEMPLATE.md`
2. Rename using the naming convention above
3. Fill in the fields
4. Save to `.claude/Bugs-to-Fix/`

---

## Template Overview

### BUG template fields

| Field | Purpose |
|-------|---------|
| Date Discovered | When it was found |
| Severity | HIGH / MEDIUM / LOW |
| Status | Current state |
| Category | The prefix category |
| Problem | User's description — capture their words |
| Context | Session link + search terms + relevant excerpt |
| Impact | What breaks, how often, blast radius |
| Files Involved | Checklist of files to change |
| Resolution Workflow | Technical: systematic debugging. Project: action plan. |

### ENH template fields

| Field | Purpose |
|-------|---------|
| Date Filed | When it was filed |
| Priority | HIGH / MEDIUM / LOW |
| Status | Current state |
| Category | The prefix category |
| Idea | User's description — capture their words |
| Context | Session link + search terms + relevant excerpt |
| Problem | What's currently missing or suboptimal |
| Proposed Solution | What to build or change |
| Files Involved | Checklist of files to change |
| Resolution Workflow | Technical: brainstorm + plan + implement. Project: action plan. |

---

## Session Context — Why It Matters

Every ticket includes a `Context` block:

```markdown
**Session:** `~/.claude/projects/[project-path]/[SESSION-ID].jsonl`
**Logged at:** YYYY-MM-DD HH:MM
**Search terms:** "term1", "term2", "term3"
```

This lets you (or Claude) reopen the original conversation where the issue was discovered — reading back the exact exchange rather than relying on memory. The search terms let you `grep` the JSONL for the relevant section quickly.

> **Where is the session ID?** Claude Code saves every conversation as a JSONL file at `~/.claude/projects/[encoded-project-path]/[SESSION-ID].jsonl`. When filing a ticket during a session, ask Claude to fill in the session ID automatically — it knows its own session ID.

---

## Resuming a Ticket in a New Session

To pick up a ticket in a future Claude Code session:

> "Read `.claude/Bugs-to-Fix/ARCH-ENH-001-claude-md-progressive-disclosure.md` and let's work on it."

Claude will read the ticket, load the session context if needed, and resume work using the resolution workflow in the ticket.

---

## Learnings Log

When you resolve a ticket, append an entry to `.claude/learnings/LEARNINGS.jsonl`:

```json
{"date": "2026-02-26", "session": "[SESSION_ID]", "what": "ARCH-BUG-001 — instruction skipped under implement directive", "decision_or_fix": "Moved hard stop to top of CLAUDE.md", "rationale": "Position matters — Claude skips middle-of-file instructions when given direct action commands", "watch_for": "Any instruction that requires reading before acting — always position at top", "tags": ["ARCH", "CLAUDE.md", "bug"]}
```

**Why JSONL not markdown:**
- Append-only — each line is a self-contained record, nothing can corrupt previous entries
- Schema-first — the first line defines the structure, agents always know what they're reading
- Queryable — grep or jq to find patterns across all resolved tickets
- Persists after tickets are deleted or archived — the learnings outlive the work

**To synthesize patterns:** Ask Claude: *"Read .claude/learnings/LEARNINGS.jsonl and summarize recurring root causes, fixes, and watch-fors."*

---

## Tips

- **File tickets mid-conversation** — don't wait. If something comes up, file it immediately before context is lost.
- **Capture your words verbatim** — the Problem/Idea field should sound like you, not like a ticket system. Future Claude reads this cold.
- **Keep tickets open until done** — don't delete them, update the Status field.
- **One issue per ticket** — if a bug reveals a second issue, file a second ticket.
- **Log the learning when you close the ticket** — the two-minute write-up compounds across sessions.
