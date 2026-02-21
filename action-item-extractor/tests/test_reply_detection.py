import pytest
from engine.reply_detection import ReplyDetector


@pytest.fixture
def detector():
    return ReplyDetector(
        user_identifiers=["test.user", "Test User", "TU"],
        slack_user_id="U12345TEST"
    )


class TestReplyDetector:
    def test_no_replies_means_not_answered(self, detector):
        messages = [{"Text": "Hey can you review this?", "UserName": "boss"}]
        assert detector.user_already_replied(messages) is False

    def test_substantive_reply_means_answered(self, detector):
        messages = [
            {"Text": "Should we add this feature?", "UserName": "boss"},
            {"Text": "Yes, let's add it to the next sprint. Here's the approach I'd recommend for implementation.", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is True

    def test_deferral_reply_means_not_answered(self, detector):
        messages = [
            {"Text": "Can you review the spec?", "UserName": "boss"},
            {"Text": "I'll look at this later today", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is False

    def test_short_acknowledgment_means_not_answered(self, detector):
        messages = [
            {"Text": "Please update the ticket", "UserName": "boss"},
            {"Text": "Noted", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is False

    def test_resolution_word_means_answered(self, detector):
        messages = [
            {"Text": "Is this done?", "UserName": "boss"},
            {"Text": "Done", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is True

    def test_lgtm_means_answered(self, detector):
        messages = [
            {"Text": "Here's the PR for review", "UserName": "dev"},
            {"Text": "LGTM", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is True

    def test_will_circle_back_means_not_answered(self, detector):
        messages = [
            {"Text": "Need your input on pricing", "UserName": "sales"},
            {"Text": "Will circle back on this tomorrow", "UserName": "test.user", "UserId": "U12345TEST"}
        ]
        assert detector.user_already_replied(messages) is False

    def test_matches_by_real_name(self, detector):
        messages = [
            {"Text": "Question for you", "UserName": "boss"},
            {"Text": "The answer is X because Y", "UserName": "someone", "RealName": "Test User", "UserId": ""}
        ]
        assert detector.user_already_replied(messages) is True
