# Beginner Setup Guide

**Time needed:** 20-30 minutes (one-time setup, then it runs automatically)

This guide assumes you have **zero experience** with GitHub, Python, YAML, or the command line. Every step is spelled out. If something doesn't match what you see on screen, stop and ask for help before continuing.

---

## What You're Setting Up

The Action Item Extractor scans your Slack messages and meeting transcripts, figures out which ones need your attention, and writes a daily action item list. It runs automatically in the background on your Mac.

**You configure two files:**
- **persona.yaml** -- Who you are, what projects you own, what topics matter to you, who always gets your attention
- **config.yaml** -- Where to scan (Slack token, file paths) and where to write output

After setup, it runs on autopilot. You just read the output.

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] A Mac (this guide is for macOS)
- [ ] Your Mac's admin password (you'll need it once for Homebrew)
- [ ] Your Slack workspace (you'll need to create a Slack app token)
- [ ] An Anthropic API key (if you have a Teams or Max subscription, your plan includes this -- see Part 8)
- [ ] 30 uninterrupted minutes

---

## Part 1: Open the Terminal

The Terminal is where you'll type commands. It's already on your Mac.

1. Press **Command + Space** (opens Spotlight search)
2. Type **Terminal**
3. Press **Enter**

A window will open with a blinking cursor. This is where you'll paste the commands below.

**Tip:** To paste into Terminal, use **Command + V** (same as anywhere else).

---

## Part 2: Install Homebrew

Homebrew is a tool that installs other tools on your Mac. You only need to do this once.

**Check if you already have it:**
```bash
brew --version
```

If you see a version number (like `Homebrew 4.x.x`), skip to Part 3.

If you see "command not found," install it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It will ask for your Mac password. **When you type your password, nothing will appear on screen** -- that's normal. Just type it and press Enter.

When it finishes, it may show instructions to "add Homebrew to your PATH." If you see something like:

```
==> Next steps:
- Run these commands in your terminal:
  echo >> /Users/YOURNAME/.zprofile
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/YOURNAME/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Copy and paste those exact commands** (the ones starting with `echo` and `eval`), one at a time.

**Verify it worked:**
```bash
brew --version
```

You should see a version number.

---

## Part 3: Install Python 3

**Check if you already have it:**
```bash
python3 --version
```

If you see `Python 3.10` or higher, skip to Part 4.

If not, install it:

```bash
brew install python@3.12
```

**Verify:**
```bash
python3 --version
```

You should see `Python 3.12.x` (or similar).

---

## Part 4: Install Git

Git is how you download the project code.

**Check if you already have it:**
```bash
git --version
```

If you see a version number, skip to Part 5.

If your Mac asks to install "command line developer tools," click **Install** and wait for it to finish. Then try `git --version` again.

If it still doesn't work:
```bash
brew install git
```

---

## Part 5: Download the Project

This downloads the action-item-extractor code to your Mac.

```bash
cd ~/Projects
```

If you get "No such file or directory," create the folder first:
```bash
mkdir -p ~/Projects
cd ~/Projects
```

Now download the code:
```bash
git clone https://github.com/pfallonjensen/action-item-extractor.git
cd action-item-extractor
```

**Verify you're in the right place:**
```bash
ls
```

You should see files like `README.md`, `persona.example.yaml`, `config.example.yaml`, and folders like `engine/`, `sources/`, `outputs/`.

---

## Part 6: Set Up Python Environment

This creates an isolated Python environment for the project (so it doesn't affect anything else on your Mac).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**You'll know it worked when:**
- Your terminal prompt now starts with `(venv)` -- this means the environment is active
- The `pip install` command printed a bunch of "Installing..." lines and finished without errors

**Important:** Every time you open a new Terminal window to work on this project, you'll need to run:
```bash
cd ~/Projects/action-item-extractor
source venv/bin/activate
```

---

## Part 7: Create Your Persona File

This is the most important step. The persona file tells the system who you are and what matters to you.

```bash
cp persona.example.yaml persona.yaml
```

Now open it in a text editor. Use TextEdit (built into your Mac):

```bash
open -a TextEdit persona.yaml
```

**If TextEdit opens in "rich text" mode** (with formatting options), switch to plain text: go to Format menu > Make Plain Text. This is important -- YAML files must be plain text.

Alternatively, if you have VS Code installed:
```bash
code persona.yaml
```

### What to Fill In

The file has clear sections with comments (lines starting with `#`). Here's what to change:

**identity section:**
```yaml
identity:
  name: "Your Full Name"
  aliases: ["FirstName", "Initials", "slack.username"]
  slack_user_id: "UXXXXXXXXXX"
  role: "Your Job Title"
```

- **name:** Your full name as it appears in Slack
- **aliases:** How people refer to you in messages (first name, initials, Slack username). The system uses these to detect when someone is talking about you.
- **slack_user_id:** Your Slack user ID (see "How to Find Your Slack User ID" below)
- **role:** Your title -- used to help the AI understand your level of responsibility

**projects section:** List each project/area you're involved in. For each one, set:
- **extract_level: all** -- you're deeply involved, extract everything relevant
- **extract_level: strategic_only** -- someone else handles day-to-day, only surface critical/high-priority items
- **extract_level: awareness_only** -- just flag items, don't create tasks

**priority_contacts section:** List people whose messages should always be extracted (your boss, board members, key stakeholders, direct reports).

**themes section:** These are already pre-filled with common themes (blocking, strategic, customer, revenue, etc.). You can add keywords that are specific to your business.

**skip_keywords section:** Words that signal something is too low-priority to extract.

Save and close the file when done.

### How to Find Your Slack User ID

1. Open Slack (desktop or web)
2. Click on your own name or profile picture
3. Click **"View full profile"**
4. Click the **three dots** (...) menu
5. Click **"Copy member ID"**

It looks like `U08XXXXXXXX`.

---

## Part 8: Create Your Config File

This file has your credentials and tells the system where to scan and where to write output.

```bash
cp config.example.yaml config.yaml
open -a TextEdit config.yaml
```

### Slack Setup

To scan Slack, you need a Slack User Token. Here's how to get one:

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. Name it something like "Action Item Extractor"
5. Select your workspace
6. Click **"Create App"**
7. In the left sidebar, click **"OAuth & Permissions"**
8. Scroll to **"User Token Scopes"** and add these scopes:
   - `channels:history`
   - `channels:read`
   - `groups:history`
   - `groups:read`
   - `im:history`
   - `im:read`
   - `mpim:history`
   - `mpim:read`
   - `users:read`
9. Scroll back up and click **"Install to Workspace"**
10. Click **"Allow"**
11. Copy the **"User OAuth Token"** (starts with `xoxp-`)

Paste that token into your config.yaml:

```yaml
sources:
  slack:
    enabled: true
    type: slack
    token: "xoxp-YOUR-TOKEN-HERE"
    workspace: "your-workspace"
    lookback_hours: 24
```

### Meeting Transcripts (Optional)

If you have meeting transcripts saved as text files on your Mac:

```yaml
  meetings:
    enabled: true
    type: local_files
    path: "/Users/YOURNAME/path/to/transcripts"
    file_patterns: ["*.txt", "*.md"]
    lookback_hours: 48
```

Replace the path with wherever your transcripts are saved. If you use Gemini for meeting notes, these get saved as `.txt` files.

If you don't have local transcripts, set `enabled: false`.

### Output Setup

**For simple markdown files** (recommended for beginners):

```yaml
output:
  type: markdown
  path: "/Users/YOURNAME/Documents/ActionItems"
```

The system will create daily files like `2026-02-19 - Action Items.md` in that folder.

**For CSV** (if you want to import into a spreadsheet):

```yaml
output:
  type: csv
  path: "/Users/YOURNAME/Documents/ActionItems"
```

### AI Processing

The extractor has three modes for AI processing. Choose one:

**Option 1: Claude Code triage (recommended -- $0 extra cost)**

If you have [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed with a Teams, Max, or Pro subscription, the AI triage uses your existing subscription at no extra cost. This is the most powerful mode -- it catches implied asks, contextual blockers, and inferred urgency that keyword matching misses.

```yaml
ai:
  triage_mode: "claude_code"
  confidence_threshold: 0.7
```

To install Claude Code: `npm install -g @anthropic-ai/claude-code`

**Option 2: Anthropic API (pay-per-use)**

If you prefer API-based processing (~$0.01-0.05 per run):

1. Go to https://console.anthropic.com/settings/keys
2. Create an API key (starts with `sk-ant-`)
3. Add to config.yaml:

```yaml
ai:
  triage_mode: "api"
  api_key: "sk-ant-YOUR-KEY-HERE"
  model: "claude-sonnet-4-5-20250929"
  confidence_threshold: 0.7
```

**Option 3: No AI (keyword-only)**

```yaml
ai:
  triage_mode: "none"
```

Save and close the file.

**Security note:** The `config.yaml` file contains your API keys. It's already in `.gitignore` so it won't be shared, but don't send this file to anyone.

---

## Part 9: Test It

Make sure everything works before setting up automation.

### Test Step 1: Data Collection (Python)

This verifies your Slack token, file paths, and persona config work:

```bash
cd ~/Projects/action-item-extractor
source venv/bin/activate

python3 collect.py /tmp/action-item-candidates
```

**What you should see:**
- A line like: `Collected 350 raw -> 280 candidates -> /tmp/action-item-candidates`
- No error messages (red text or "Traceback")

**If you see errors:**
- `FileNotFoundError: persona.yaml` -- Make sure you're in the right directory
- `slack_api_error` -- Double-check your Slack token in config.yaml
- `No module named 'engine'` -- Make sure you activated the virtual environment (`source venv/bin/activate`)

### Test Step 2: Full Pipeline (Python + Claude Code)

This runs the complete two-step pipeline -- Python collection followed by Claude Code AI triage:

```bash
./run-extract-tasks.sh
```

**What you should see:**
- Step 1 collects candidates (same as above)
- Step 2 runs Claude Code triage -- you'll see it processing and writing output
- A new action items file in your output folder

**If Step 2 fails:**
- `Claude CLI not found` -- Install Claude Code: `npm install -g @anthropic-ai/claude-code`
- `OAuth token expired` -- Open Claude Code interactively (`claude`) to refresh your token, or set `ANTHROPIC_API_KEY` in a `.env` file
- If you don't have Claude Code and don't want to install it, set `triage_mode: "none"` in config.yaml to use keyword-only mode

### Alternative: Keyword-Only Mode (No Claude Code)

If you don't have Claude Code installed, you can run the keyword-only pipeline:

```bash
./automation/run.sh
```

This uses Python's rule-based filtering instead of AI triage. It catches ~60% of what the AI catches -- good for getting started, but you'll miss implied asks and contextual items.

---

## Part 10: Set Up Automatic Scheduling (Optional)

This makes the extractor run automatically throughout the day without you doing anything.

### Option A: macOS LaunchAgent (Recommended)

1. Copy the template:
```bash
cp automation/launchagent.example.plist ~/Library/LaunchAgents/com.action-item-extractor.plist
```

2. Open it for editing:
```bash
open -a TextEdit ~/Library/LaunchAgents/com.action-item-extractor.plist
```

3. Find and replace these placeholders:
   - Replace `/path/to/action-item-extractor` with `/Users/YOURNAME/Projects/action-item-extractor`
   - Replace `YOURNAME` with your Mac username (check with: `whoami`)
   - The `ProgramArguments` should point to `run-extract-tasks.sh` (two-step pipeline) or `automation/run.sh` (keyword-only)

4. Save and close the file

5. Load the schedule:
```bash
launchctl load ~/Library/LaunchAgents/com.action-item-extractor.plist
```

It will now run at the times specified in the plist file (default: 6am, 11am, 3pm, 6pm).

**To stop automatic runs:**
```bash
launchctl unload ~/Library/LaunchAgents/com.action-item-extractor.plist
```

### Option B: Run Manually

If you prefer to run it yourself when you want, just open Terminal and run:

```bash
cd ~/Projects/action-item-extractor
./run-extract-tasks.sh
```

---

## Part 11: Read Your Action Items

After the extractor runs, check your output folder:

**If you chose markdown output:**
Open `/Users/YOURNAME/Documents/ActionItems/` in Finder. You'll see daily files with your extracted action items, organized by priority.

**If you chose CSV output:**
Open the CSV file in Excel or Google Sheets.

**If you chose Obsidian output:**
Open Obsidian and navigate to the Action Items folder in your vault.

---

## Updating the Project

When improvements are made to the extractor, you can get the latest version:

```bash
cd ~/Projects/action-item-extractor
git pull
source venv/bin/activate
pip install -r requirements.txt
```

Your `persona.yaml` and `config.yaml` files won't be overwritten -- they're yours.

---

## Troubleshooting

### "command not found: python3"
Run `brew install python@3.12` and try again.

### "command not found: git"
Your Mac should prompt you to install developer tools. Click Install. If not, run `brew install git`.

### "No module named 'engine'"
You forgot to activate the virtual environment. Run `source venv/bin/activate` first.

### "Permission denied"
Add `sudo` before the command and enter your Mac password. Example: `sudo brew install python@3.12`

### "invalid_api_key" from Anthropic
Go to https://console.anthropic.com/settings/keys, create a new key, and update it in `config.yaml`. If you have a Teams/Max subscription, make sure you're logged in with the same account.

### Slack token not working
Make sure you copied the **User OAuth Token** (starts with `xoxp-`), not the Bot Token. Also verify you added all the required scopes listed in Part 8.

### The extractor runs but finds 0 items
- Check that your Slack token has the right scopes
- Make sure your persona.yaml has realistic keywords that match your actual Slack conversations
- Try increasing `lookback_hours` to 48 or 72 for the first run

### LaunchAgent isn't running
Check if it's loaded: `launchctl list | grep action-item`
If nothing shows, re-run the `launchctl load` command from Part 10.

---

## Quick Reference

| Task | Command |
|------|---------|
| Run the extractor (AI triage) | `cd ~/Projects/action-item-extractor && ./run-extract-tasks.sh` |
| Run the extractor (keyword-only) | `cd ~/Projects/action-item-extractor && ./automation/run.sh` |
| Update to latest version | `cd ~/Projects/action-item-extractor && git pull && source venv/bin/activate && pip install -r requirements.txt` |
| Edit your persona | `open -a TextEdit ~/Projects/action-item-extractor/persona.yaml` |
| Edit your config | `open -a TextEdit ~/Projects/action-item-extractor/config.yaml` |
| Check automation logs | `cat ~/Projects/action-item-extractor/extract-tasks.log` |
| Stop automation | `launchctl unload ~/Library/LaunchAgents/com.action-item-extractor.plist` |
| Start automation | `launchctl load ~/Library/LaunchAgents/com.action-item-extractor.plist` |

---

## Getting Help

- **README.md** in the project folder has the full technical documentation
- **examples/** folder has persona configs for different roles (VP Product, Engineering Manager, CEO)
- Open an issue at the GitHub repo for bugs or feature requests
