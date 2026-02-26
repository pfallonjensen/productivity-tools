# {PREFIX}-BUG-{NUM}: {Title}

**Date Discovered:** YYYY-MM-DD
**Severity:** HIGH | MEDIUM | LOW
**Status:** OPEN
**Category:** {ARCH | SKILLS | AUTO | HOOKS | MEM | YOUR-CATEGORY}

---

## Problem

[User's description — minimal editing, capture their words]

---

## Context

**Session:** `~/.claude/projects/[encoded-project-path]/[SESSION-ID].jsonl`
**Logged at:** YYYY-MM-DD HH:MM
**Search terms:** "term1", "term2", "term3"

### Relevant Excerpt

**User:**
> [The user's complaint/observation that triggered this]

**Claude output or behavior that triggered this:**
```
[The specific output or behavior that was wrong, if applicable]
```

---

## Impact

What breaks, how often, what's the blast radius.

---

## Files Involved

- [ ] `path/to/file` — what needs to change

---

## Resolution Workflow

### For technical categories (ARCH, SKILLS, AUTO, HOOKS, MEM, and similar):

**1. Root Cause Investigation**
```
/superpowers:systematic-debugging
```
Follow Phase 1-4. NO fixes until root cause identified.

**2. Implementation**
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Verified working
- [ ] Status updated to DONE
- [ ] Learning logged → append to `.claude/learnings/LEARNINGS.jsonl`:
  ```json
  {"date": "YYYY-MM-DD", "session": "[SESSION_ID]", "what": "[ticket ID + title]", "decision_or_fix": "[what fixed it]", "rationale": "[why root cause + why this fix]", "watch_for": "[failure mode to watch for]", "tags": ["[PREFIX]", "bug"]}
  ```

### For project categories (customize these):

**Action Plan**
- [ ] Step 1
- [ ] Step 2
- [ ] Done

---

*Filed: YYYY-MM-DD*
