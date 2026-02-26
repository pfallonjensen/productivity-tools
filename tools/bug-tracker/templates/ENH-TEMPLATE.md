# {PREFIX}-ENH-{NUM}: {Title}

**Date Filed:** YYYY-MM-DD
**Priority:** HIGH | MEDIUM | LOW
**Status:** OPEN
**Category:** {ARCH | SKILLS | AUTO | HOOKS | MEM | YOUR-CATEGORY}

---

## Idea

[User's description — minimal editing, capture their words]

---

## Context

**Session:** `~/.claude/projects/[encoded-project-path]/[SESSION-ID].jsonl`
**Logged at:** YYYY-MM-DD HH:MM
**Search terms:** "term1", "term2", "term3"

### Relevant Excerpt

**User:**
> [The user's idea/observation that triggered this]

**Discussion context:**
```
[Any relevant context from the conversation]
```

---

## Problem

What's currently missing, broken, or suboptimal that this addresses.

---

## Proposed Solution

Concrete description of what to build or change.

---

## Files Involved

- [ ] `path/to/file` — what changes

---

## Resolution Workflow

### For technical categories (ARCH, SKILLS, AUTO, HOOKS, MEM, and similar):

**1. Design**
```
/superpowers:brainstorming
```
Explore the idea. What's the best approach? What are the trade-offs?

**2. Planning**
```
/superpowers:writing-plans
```
For multi-step implementations.

**3. Implementation**
- [ ] Approach decided
- [ ] Implemented
- [ ] Verified working
- [ ] Status updated to DONE
- [ ] Learning logged → append to `.claude/learnings/LEARNINGS.jsonl`:
  ```json
  {"date": "YYYY-MM-DD", "session": "[SESSION_ID]", "what": "[ticket ID + title]", "decision_or_fix": "[what was built]", "rationale": "[why this approach over alternatives]", "watch_for": "[failure modes, edge cases]", "tags": ["[PREFIX]", "enh"]}
  ```

### For project categories (customize these):

**Action Plan**
- [ ] Step 1
- [ ] Step 2
- [ ] Done

---

*Filed: YYYY-MM-DD*
