"""
Smart reply detection — determines if user has already substantively replied.
Ported from slack_scanner.py to be generic and persona-driven.
"""
from typing import List


# Resolution words — short replies that count as answered
RESOLUTION_WORDS = {
    "done", "fixed", "yes", "no", "lgtm", "approved", "completed",
    "merged", "shipped", "resolved", "confirmed", "acknowledged"
}

# Explanation starters — indicate substantive response
EXPLANATION_STARTERS = [
    "here's", "the reason is", "the answer is", "my recommendation",
    "i think we should", "i suggest", "i recommend", "let me explain",
    "the approach", "we should", "let's go with", "i've updated",
    "i've created", "i've added", "i've fixed"
]

# Deferral phrases — user acknowledged but hasn't actually done the work
DEFERRAL_PHRASES = [
    "i'll look at", "will review", "let me check", "i'll get to",
    "i'll get back", "adding to my list", "will circle back",
    "i'll take a look", "will do", "on my radar", "i'll handle",
    "will get to this", "let me get back", "noted, will",
    "i'll follow up", "will address"
]

# Short acknowledgments that don't count as substantive
SHORT_ACKNOWLEDGMENTS = [
    "ok", "okay", "thanks", "thank you", "got it", "noted",
    "understood", "ack", "roger", "copy", "k", "kk", "thx", "ty"
]

# Minimum length for a non-resolution reply to be "substantive"
MIN_SUBSTANTIVE_LENGTH = 50


class ReplyDetector:
    """Detects whether a user has already substantively replied to a thread."""

    def __init__(self, user_identifiers: List[str], slack_user_id: str = ""):
        self.user_identifiers = [uid.lower() for uid in user_identifiers]
        self.slack_user_id = slack_user_id

    def user_already_replied(self, messages: List[dict]) -> bool:
        """
        Check if the user has substantively replied in a message thread.

        A reply is substantive if:
        - Contains a resolution word (Done, LGTM, etc.)
        - Contains an explanation starter (Here's, The reason is, etc.)
        - Is long enough (>50 chars) AND doesn't contain deferral language

        A reply is NOT substantive if:
        - Contains deferral phrases (I'll look at, Will review, etc.)
        - Is a short acknowledgment (Ok, Thanks, Noted)
        - Is < 50 chars without resolution words
        """
        for msg in messages:
            if not self._is_from_user(msg):
                continue
            if self._is_substantive_reply(msg.get("Text", "")):
                return True
        return False

    def _is_from_user(self, msg: dict) -> bool:
        """Check if a message is from the tracked user."""
        # Check by Slack user ID
        if self.slack_user_id and msg.get("UserId") == self.slack_user_id:
            return True

        # Check by username
        username = msg.get("UserName", "").lower()
        if username in self.user_identifiers:
            return True

        # Check by real name
        real_name = msg.get("RealName", "").lower()
        if real_name and real_name in self.user_identifiers:
            return True

        return False

    def _is_substantive_reply(self, text: str) -> bool:
        """Determine if a reply is substantive (not just acknowledgment/deferral)."""
        text_lower = text.lower().strip()

        # Check for deferral phrases FIRST (overrides length and explanation)
        for phrase in DEFERRAL_PHRASES:
            if phrase in text_lower:
                return False

        # Check for resolution words (even short replies count)
        words = set(text_lower.split())
        if words & RESOLUTION_WORDS:
            return True

        # Check for explanation starters
        for starter in EXPLANATION_STARTERS:
            if starter in text_lower:
                return True

        # Short acknowledgment check
        if len(text_lower) < MIN_SUBSTANTIVE_LENGTH:
            # Short reply without resolution word = not substantive
            return False

        # Long reply without deferral = substantive
        return True
