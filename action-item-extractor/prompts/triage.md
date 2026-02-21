# Triage Extract — AI Semantic Triage

You are performing semantic triage on pre-collected, pre-filtered action item candidates.

## Step 0: Fetch Google Sources via MCP (before triaging)

Before processing the candidates JSON, fetch additional items from Google sources using MCP tools. These supplement the Slack + meetings data already collected by Python.

### Gmail (work inbox — last 24 hours)

1. Use `mcp__google-workspace__search_gmail_messages` with:
   - `query`: `newer_than:1d -category:promotions -category:social -category:updates`
   - `user_google_email`: read from persona JSON `identity.email`
   - `page_size`: 25
2. For messages found, use `mcp__google-workspace__get_gmail_messages_content_batch` to get full content
3. Convert each email to a candidate object:
   ```json
   {"content": "Subject: {subject}\n\nFrom: {sender}\n\n{body}", "author": "{sender_name}", "timestamp": "{date}", "source_type": "email", "source_url": "{gmail_link}", "metadata": {"provider": "gmail", "thread_id": "{thread_id}", "force_keep": false, "matched_themes": []}}
   ```
4. Add these candidates to the list from the JSON file

### Google Docs (optional — if document_id in persona config)

If the persona config includes Google Docs sources, use `mcp__google-workspace__get_doc_as_markdown` to fetch content and add as candidates.

**If MCP tools are unavailable or fail**: proceed with the candidates JSON only. Google sources are supplementary — Slack and meetings are the core sources.

## Step 1: Carry Forward Incomplete Items

Before triaging new candidates, check for incomplete action items from previous days that should be carried forward.

### How to carry forward:

1. Read the output config from the candidates JSON (the `output` object) to get the vault `path` and `action_items_path`. If the `output` object is empty or missing, look for common Obsidian vault paths: check if `/Users/fallonjensen/Obsidian Vault/Daybreak/Action Items/` exists, or ask the user.
2. Use Glob to find the most recent previous action items file:
   - Pattern: `{path}/{action_items_path}/*Action Items.md`
   - Look for the file with the most recent date BEFORE today
   - Try up to 7 days back (weekends/gaps are normal)
3. Read that file and extract all **unchecked** items: lines matching `- [ ]` (NOT `- [x]`)
4. Skip any items inside a `## ✅ RESOLVED` section (everything below that heading)
5. For each carried-forward item, track:
   - Original text (preserve the full item including sub-bullets with context)
   - Original priority marker (⏫, 🔼, 🔽)
   - How many days it's been open (calculate from the file's date)
6. When writing today's output file, include carried-forward items in a `## ⏳ Carried Forward` section at the TOP (before source-specific sections)
7. **Deduplication**: If a newly triaged candidate matches a carried-forward item (same task, same requestor, same ticket), keep ONLY the new version (it has fresher context). Remove the duplicate from the carried-forward list.
8. Items carried forward 3+ days should be marked with `⚠️ OVERDUE (N days)` after the priority emoji

### Carried-forward output format:
```markdown
## ⏳ Carried Forward
*{N} incomplete items from {previous_date}*

- [ ] Original task text ⏫ #project-tag
  - **Requested by:** Original requestor
  - **Context:** Original context
  - **Originally from:** {source} ({original_date})
```

**If no previous file exists or all items are checked off**: skip this step, no carried-forward section.

## Input

Read the candidates JSON file at: `__BATCH_FILE__`

The JSON has this structure:
```json
{
  "persona": { "identity": {...}, "projects": {...}, "themes": {...}, ... },
  "output": { "path": "...", "action_items_path": "...", ... },
  "candidates": [ { "content": "...", "author": "...", "timestamp": "...", "source_type": "...", "source_url": "...", "metadata": {...} }, ... ],
  "stats": { "raw_items": N, "after_noise_filter": N }
}
```

Combine the Python-collected candidates with any Google-sourced candidates from Step 0, then triage everything together.

## Your Job

For each candidate, make a **keep/skip decision** with reasoning:

### KEEP if:
1. **Explicit ask directed at the persona** — someone asked them to do something, review something, approve something
2. **Implied ask** — context makes clear their input is needed even without direct request (e.g., "we're stuck on the spec" in a channel where they're the PM)
3. **Blocking item** — team can't proceed without this person's decision/input
4. **Strategic decision needed** — roadmap, prioritization, scope, go/no-go
5. **Customer-critical** — escalation, requirements, churn risk, relationship items
6. **Revenue/business** — pricing, deals, contracts, expansion
7. **Risk item** — delivery gaps, SLA risk, quality issues they should know about
8. **Ticket assignment** — tickets mentioned with assignees (extract individual grooming tasks for ALL tickets)

### SKIP if:
1. **No action needed from persona** — purely informational, FYI with no ask
2. **Already handled** — thread shows persona already substantively replied (not just "noted" or "I'll look at it")
3. **Wrong audience** — item is for someone else, persona not relevant
4. **Low-impact operational** — minor bugs, typos, formatting (already pre-filtered, but double-check)
5. **Duplicate of another candidate** — same ask from different angle

### CRITICAL — Catch What Keywords Miss:
The whole point of AI triage is catching things keyword matching misses:
- **Implied asks**: "The design is ready for the dashboard feature" → implies persona needs to review it
- **Contextual blockers**: "We can't move forward until the requirements are clearer" → persona is the PM, this blocks them
- **Inferred urgency**: "Go-live is Friday and we still don't have sign-off" → time-sensitive
- **Subtext**: "It would be helpful to get alignment on the approach" → diplomatic ask for decision
- **Two-way workflow**: Check if persona was asked something AND already answered (skip if answered substantively)

### Items tagged `force_keep: true`:
Always extract these — they were flagged because the persona was directly mentioned or a priority contact sent them.

## Output Format

For each **kept** item, extract a structured task and write it to the output. Use the Obsidian output format.

Read the output config from the candidates JSON `output` object:
- `path`: the vault root path
- `action_items_path`: relative path within the vault for action item files

Write to: `{path}/{action_items_path}/{YYYY-MM-DD} - Action Items.md`
Also write source-specific files: `{path}/{action_items_path}/By Source/From {source_type}/{YYYY-MM-DD}.md`

### File Structure:

**IMPORTANT**: If today's file already exists, READ it first. Merge new items with existing items — do NOT overwrite carried-forward items or items from a previous triage run. Add new items to the appropriate sections and update the header stats.

```markdown
# Action Items - {YYYY-MM-DD}
*Extracted: {YYYY-MM-DD} {HH:MM}*
*Total: {N} tasks ({M} new, {K} carried forward)*

## ⏳ Carried Forward
*{K} incomplete items from {previous_date}*

{carried-forward items here — see Step 1}

## 📝 From Meetings

### High Priority (⏫)
{high priority meeting items}

### Medium Priority (🔼)
{medium priority meeting items}

### Low Priority (🔽)
{low priority meeting items}

## 💬 From Slack

### High Priority (⏫)
{high priority slack items}

### Medium Priority (🔼)
{medium priority slack items}

## 📧 From Email
{email items if any}

## 🎫 From Jira
{jira items if any — or "*(Not scanned this run)*" if no Jira source}
```

### Task Format:
```markdown
- [ ] {title} {priority_emoji} #{project-tag}
  - **Requested by:** {requestor}
  - **Context:** {context/description}
  - **Why extracted:** {reason for keeping — be specific}
  - **Source:** {source name} ({date})
```

If source URLs are available, include a link:
```markdown
  - **Link:** [{source_type} Message]({source_url})
```

## Smart Reply Detection

When evaluating thread context:
- **Substantive reply** (skip): Contains resolution words (done, fixed, LGTM, approved), detailed explanation (>100 chars without deferral), or specific recommendations
- **Non-substantive** (still extract): "I'll look at it", "Noted", "Will review later", short acknowledgments
- Check the `metadata.thread_context` field if available

## Ticket Intelligence

When messages mention tickets (e.g., DDS-485, DDS-486):
- Extract **individual grooming tasks** for ALL tickets mentioned
- Detect assignees: "Shivam will pick up DDS-485" → assignee: Shivam
- If persona is PM for the project, they need to groom ALL tickets before team picks them up

## Project-Aware Filtering

Use the persona's project definitions:
- **extract_level: all** → extract high-leverage + PM work
- **extract_level: strategic_only** → extract only critical/high priority themes
- **extract_level: awareness_only** → should already be filtered out, but skip if not

## Jira Scanning

If a Jira source is configured in the candidates JSON (or if the persona has Jira project keys), scan for recently assigned or updated tickets:
- Check for tickets assigned to the persona in their projects (use persona `projects` keys)
- Focus on tickets updated in the last 7 days with status changes, new comments, or assignments
- If no Jira source is available or configured, write `*(Not scanned this run)*` in the Jira section

**Note**: Jira scanning may be handled by the Python collection step (if `jira` source is enabled in config.yaml) or via Jira MCP tools if available. If neither is available, skip gracefully.

## Stats Output

After processing, print a summary:
```
Triage complete: {kept}/{total} candidates kept
  - force_keep: {N}
  - semantic_keep: {N}  (caught by AI, not keyword-matched)
  - skipped: {N}
  - carried_forward: {N}  (from previous day)
Output written to: {file_path}
```
