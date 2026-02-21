import pytest
from engine.ticket_parser import TicketParser


@pytest.fixture
def parser():
    return TicketParser(pattern=r'[A-Z]{2,5}-\d{1,5}')


class TestTicketParser:
    def test_finds_tickets(self, parser):
        tickets = parser.find_tickets("Check PROJ-485 and PROJ-486")
        assert [t['ticket'] for t in tickets] == ['PROJ-485', 'PROJ-486']

    def test_deduplicates_tickets(self, parser):
        tickets = parser.find_tickets("PROJ-485 is blocked. PROJ-485 needs review.")
        assert len(tickets) == 1

    def test_detects_assignee_will_pick_up(self, parser):
        tickets = parser.find_tickets("Alice will pick up PROJ-485.")
        assert tickets[0]['assignee'] == 'Alice'

    def test_detects_assignee_taken_by(self, parser):
        tickets = parser.find_tickets("PROJ-455 will be taken by Bob.")
        assert tickets[0]['assignee'] == 'Bob'

    def test_no_assignee_when_none_mentioned(self, parser):
        tickets = parser.find_tickets("Please groom PROJ-486")
        assert tickets[0]['assignee'] is None

    def test_custom_pattern_github_issues(self):
        parser = TicketParser(pattern=r'#\d+')
        tickets = parser.find_tickets("Fix #123 and #456")
        assert [t['ticket'] for t in tickets] == ['#123', '#456']

    def test_extracts_ticket_title_parentheses(self, parser):
        tickets = parser.find_tickets("PROJ-455 (Decision Log) needs grooming")
        assert tickets[0].get('title_hint') == 'Decision Log'

    def test_empty_text(self, parser):
        assert parser.find_tickets("") == []
