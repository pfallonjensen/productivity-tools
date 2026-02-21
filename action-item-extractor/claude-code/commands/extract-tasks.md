# Extract Tasks Command

Run the action item extraction pipeline with your configured sources and output.

## Usage

```
/extract-tasks
```

## What It Does

1. Loads your `persona.yaml` (identity, projects, themes) and `config.yaml` (sources, output, AI)
2. Scans all enabled sources for recent messages
3. Filters using your extraction rules (mentions, priority contacts, themes, project levels)
4. Deduplicates across sources
5. Enriches with AI (titles, priorities, due dates)
6. Saves to your configured output (Obsidian, markdown, or CSV)

## Prerequisites

1. Copy `persona.example.yaml` to `persona.yaml` and fill out your identity, projects, themes
2. Copy `config.example.yaml` to `config.yaml` and add your credentials
3. Install dependencies: `pip install -r requirements.txt`

## Options

Run with custom config paths:
```bash
./automation/run.sh -p /custom/persona.yaml -c /custom/config.yaml
```
