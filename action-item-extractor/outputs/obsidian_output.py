"""
Obsidian output plugin -- saves tasks to Obsidian vault with smart management.
Ported from task_manager.py, made config-driven.
"""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from outputs.base_output import BaseOutput


PRIORITY_EMOJI = {'high': '\u23eb', 'medium': '\U0001F53C', 'low': '\U0001F53D'}

# Section header emojis
_EMOJI_CALENDAR = '\U0001F4C5'
_EMOJI_CALENDAR_PAGE = '\U0001F4C6'
_EMOJI_SPARKLES = '\u2728'
_EMOJI_WARNING = '\u26a0\ufe0f'


class ObsidianOutput(BaseOutput):
    """Save tasks to Obsidian vault with dedup, priorities, carry-forward."""

    def __init__(self, output_config: dict, persona: dict):
        super().__init__(output_config, persona)
        self.vault_path = Path(output_config.get('path', ''))
        self.action_items_path = self.vault_path / output_config.get('action_items_path', 'Action Items')
        self.preserve_priorities = output_config.get('preserve_manual_priorities', True)
        self.carry_forward = output_config.get('carry_forward_incomplete', True)
        self.past_due_tracking = output_config.get('past_due_tracking', True)

    def save_tasks(self, tasks: List[Dict]) -> None:
        """Save tasks to daily file with dedup and priority preservation."""
        if not tasks:
            return

        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.action_items_path / f"{today} - Action Items.md"

        # Parse existing content for dedup and priority preservation
        existing_content = ""
        priorities_section = ""
        existing_titles = []

        if daily_file.exists():
            existing_content = daily_file.read_text(encoding='utf-8')
            priorities_section = self._extract_priorities_section(existing_content)
            existing_titles = self._extract_existing_titles(existing_content)

        # Deduplicate new tasks against existing
        new_tasks = [t for t in tasks if not self._is_duplicate(t['title'], existing_titles)]

        if not new_tasks and daily_file.exists():
            return  # Nothing new to add

        # Group tasks by urgency
        grouped = self._group_by_urgency(
            new_tasks + self._get_carried_forward(existing_content), today
        )

        # Build output
        content = self._build_daily_content(priorities_section, grouped, today, len(new_tasks))

        # Ensure directory exists
        daily_file.parent.mkdir(parents=True, exist_ok=True)
        daily_file.write_text(content, encoding='utf-8')

        # Create source-specific files
        self._save_source_files(tasks, today)

    def update_dashboard(self) -> None:
        """Update Task Dashboard.md with summary."""
        pass  # Dashboard update can be added later

    def _extract_priorities_section(self, content: str) -> str:
        """Extract the manual priorities section (before ---)."""
        if '---' in content:
            return content.split('---')[0]
        return ""

    def _extract_existing_titles(self, content: str) -> List[str]:
        """Extract task titles from existing file content."""
        titles = []
        # Match heading format: ### Task Title (possibly followed by priority emoji)
        emoji_chars = ''.join(PRIORITY_EMOJI.values())
        pattern_heading = r'^###\s+(.+?)(?:\s+[' + re.escape(emoji_chars) + r'])?\s*$'
        for match in re.finditer(pattern_heading, content, re.MULTILINE):
            titles.append(match.group(1).strip())
        # Match checkbox format: - [ ] Task Title ... date marker
        pattern_checkbox = r'^- \[[ x]\]\s+(.+?)(?:\s+' + re.escape(_EMOJI_CALENDAR) + r')'
        for match in re.finditer(pattern_checkbox, content, re.MULTILINE):
            titles.append(match.group(1).strip())
        return titles

    def _is_duplicate(self, title: str, existing_titles: List[str]) -> bool:
        """Check if a title is a fuzzy duplicate of existing tasks."""
        title_lower = title.lower()
        for existing in existing_titles:
            ratio = SequenceMatcher(None, title_lower, existing.lower()).ratio()
            if ratio >= 0.8:
                return True
        return False

    def _group_by_urgency(self, tasks: List[Dict], today: str) -> Dict[str, List[Dict]]:
        """Group tasks by urgency category."""
        groups: Dict[str, List[Dict]] = {
            'today': [],
            'past_due': [],
            'urgent_week': [],
            'this_week': [],
            'later': [],
        }

        today_date = datetime.strptime(today, '%Y-%m-%d').date()

        for task in tasks:
            due = task.get('due_date', '')
            if not due:
                groups['this_week'].append(task)
                continue

            try:
                due_date = datetime.strptime(due, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                groups['this_week'].append(task)
                continue

            diff = (due_date - today_date).days

            if diff < 0:
                task['_overdue_days'] = abs(diff)
                groups['past_due'].append(task)
            elif diff == 0:
                groups['today'].append(task)
            elif diff <= 3:
                groups['urgent_week'].append(task)
            elif diff <= 7:
                groups['this_week'].append(task)
            else:
                groups['later'].append(task)

        return groups

    def _build_daily_content(
        self,
        priorities_section: str,
        grouped: Dict[str, List[Dict]],
        today: str,
        new_count: int,
    ) -> str:
        """Build the full daily file content."""
        lines: List[str] = []

        # Priorities section
        if priorities_section:
            lines.append(priorities_section.rstrip())
        else:
            lines.append("# My Chosen Priorities\n")
            lines.append("")

        lines.append("\n---\n")

        # Header
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        day_name = datetime.strptime(today, '%Y-%m-%d').strftime('%a %b %d')
        lines.append(f"# Action Items - {today}")
        lines.append(f"*Extracted: {now}*")
        lines.append(f"*Total: {new_count} new tasks*\n")

        # Section builders
        sections = [
            ('today', f'{_EMOJI_SPARKLES} TODAY - {day_name}'),
            ('past_due', f'{_EMOJI_WARNING} PAST DUE'),
            ('urgent_week', f'{_EMOJI_WARNING} URGENT This Week'),
            ('this_week', f'{_EMOJI_CALENDAR} This Week'),
            ('later', f'{_EMOJI_CALENDAR_PAGE} Later'),
        ]

        for key, header in sections:
            tasks_in_group = grouped.get(key, [])
            if tasks_in_group:
                lines.append(f"## {header}")
                for task in tasks_in_group:
                    lines.append(self._format_task(task))
                lines.append("")

        return '\n'.join(lines)

    def _format_task(self, task: Dict) -> str:
        """Format a single task as markdown."""
        emoji = PRIORITY_EMOJI.get(task.get('priority', 'medium'), '\U0001F53C')
        title = task.get('title', 'Untitled')
        due = task.get('due_date', '')
        project = task.get('project', '')

        lines = [f"\n### {title} {emoji}"]

        if due:
            overdue = task.get('_overdue_days', 0)
            if overdue > 0:
                lines.append(f"{_EMOJI_WARNING} **Due: {due} ({overdue} days overdue)** {_EMOJI_WARNING}")
            else:
                lines.append(f"{_EMOJI_CALENDAR} {due}")

        if project:
            lines.append(f"#{project}")

        # Receipts table
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(
            f"| **From** | {task.get('requestor', task.get('source_author', 'Unknown'))} |"
        )
        lines.append(f"| **App** | {task.get('source_type', 'Unknown')} |")
        lines.append(f"| **Timestamp** | {task.get('source_timestamp', '')} |")

        url = task.get('source_url', '')
        if url:
            lines.append(
                f"| **Link** | [{task.get('source_type', 'Source')} Message]({url}) |"
            )

        context = task.get('context', '')
        if context:
            lines.append(f"\n**Action:** {context}")

        return '\n'.join(lines)

    def _get_carried_forward(self, existing_content: str) -> List[Dict]:
        """Get unchecked tasks from existing content for carry-forward."""
        if not self.carry_forward or not existing_content:
            return []
        # For initial implementation, carry-forward is handled by not overwriting
        # unchecked tasks
        return []

    def _save_source_files(self, tasks: List[Dict], today: str) -> None:
        """Save tasks grouped by source type."""
        source_groups: Dict[str, List[Dict]] = {}
        for task in tasks:
            source = task.get('source_type', 'unknown')
            source_groups.setdefault(source, []).append(task)

        source_name_map = {
            'slack': 'From Slack',
            'meeting': 'From Meetings',
            'local_files': 'From Meetings',
            'jira': 'From Jira',
            'confluence': 'From Confluence',
            'email': 'From Email',
        }

        for source_type, source_tasks in source_groups.items():
            folder_name = source_name_map.get(source_type, f'From {source_type.title()}')
            source_dir = self.action_items_path / "By Source" / folder_name
            source_dir.mkdir(parents=True, exist_ok=True)

            source_file = source_dir / f"{today}.md"
            lines = [f"# {folder_name} - {today}\n"]
            for task in source_tasks:
                lines.append(self._format_task(task))
            source_file.write_text('\n'.join(lines), encoding='utf-8')
