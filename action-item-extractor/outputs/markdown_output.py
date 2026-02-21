"""
Markdown output plugin — saves tasks as simple markdown files.
No Obsidian-specific syntax (no Tasks plugin format).
"""
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from outputs.base_output import BaseOutput


PRIORITY_EMOJI = {'high': '⏫', 'medium': '🔼', 'low': '🔽'}


class MarkdownOutput(BaseOutput):
    """Save tasks as simple markdown files."""

    def __init__(self, output_config: dict, persona: dict):
        super().__init__(output_config, persona)
        self.path = Path(output_config.get('path', '.'))

    def save_tasks(self, tasks: List[Dict]) -> None:
        if not tasks:
            return

        today = datetime.now().strftime('%Y-%m-%d')
        output_file = self.path / f"{today}-action-items.md"

        lines = [f"# Action Items - {today}\n"]
        lines.append(f"*Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*Total: {len(tasks)} tasks*\n")

        for task in tasks:
            emoji = PRIORITY_EMOJI.get(task.get('priority', 'medium'), '🔼')
            lines.append(f"## {task.get('title', 'Untitled')} {emoji}")
            lines.append(f"- **Priority:** {task.get('priority', 'medium')}")
            lines.append(f"- **Due:** {task.get('due_date', 'TBD')}")
            lines.append(f"- **From:** {task.get('requestor', task.get('source_author', 'Unknown'))}")
            lines.append(f"- **Project:** {task.get('project', 'General')}")
            context = task.get('context', '')
            if context:
                lines.append(f"- **Context:** {context}")
            url = task.get('source_url', '')
            if url:
                lines.append(f"- **Source:** [{task.get('source_type', 'Link')}]({url})")
            lines.append("")

        self.path.mkdir(parents=True, exist_ok=True)
        output_file.write_text('\n'.join(lines), encoding='utf-8')

    def update_dashboard(self) -> None:
        pass
