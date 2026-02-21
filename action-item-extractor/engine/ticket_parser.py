"""
Configurable ticket parser — finds ticket references and detects assignments.
Pattern is configurable via persona.yaml ticket_detection.pattern.
"""
import re
from typing import List, Optional


# Assignment patterns — match "Person will pick up TICKET" or "TICKET taken by Person"
ASSIGNMENT_PATTERNS = [
    # "Person will pick up TICKET"
    r'(\w+)\s+will\s+(?:pick\s+up|handle|take|work\s+on)\s+{ticket}',
    # "TICKET will be taken by Person"
    r'{ticket}\s+will\s+be\s+(?:taken|handled|picked\s+up)\s+by\s+(\w+)',
    # "TICKET assigned to Person"
    r'{ticket}\s+(?:assigned|given)\s+to\s+(\w+)',
    # "Person is taking TICKET"
    r'(\w+)\s+is\s+(?:taking|handling|picking\s+up)\s+{ticket}',
]


class TicketParser:
    """Finds ticket references and detects assignees in message text."""

    def __init__(self, pattern: str = r'[A-Z]{2,5}-\d{1,5}'):
        self.pattern = pattern
        self._compiled = re.compile(pattern)

    def find_tickets(self, text: str) -> List[dict]:
        """
        Find all ticket references in text with optional assignee and title hint.

        Returns list of dicts: {'ticket': str, 'assignee': str|None, 'title_hint': str|None}
        """
        if not text:
            return []

        # Find all ticket matches
        matches = self._compiled.findall(text)
        if not matches:
            return []

        # Deduplicate while preserving order
        seen = set()
        unique_tickets = []
        for ticket in matches:
            if ticket not in seen:
                seen.add(ticket)
                unique_tickets.append(ticket)

        results = []
        for ticket in unique_tickets:
            assignee = self._detect_assignee(text, ticket)
            title_hint = self._extract_title_hint(text, ticket)
            results.append({
                'ticket': ticket,
                'assignee': assignee,
                'title_hint': title_hint
            })

        return results

    def _detect_assignee(self, text: str, ticket: str) -> Optional[str]:
        """Detect who is assigned to a ticket."""
        escaped_ticket = re.escape(ticket)
        for pattern_template in ASSIGNMENT_PATTERNS:
            pattern = pattern_template.replace('{ticket}', escaped_ticket)
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_title_hint(self, text: str, ticket: str) -> Optional[str]:
        """Extract a title hint from parentheses after the ticket reference."""
        escaped_ticket = re.escape(ticket)
        match = re.search(rf'{escaped_ticket}\s*\(([^)]+)\)', text)
        if match:
            return match.group(1).strip()
        return None
