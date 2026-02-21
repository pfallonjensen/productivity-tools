"""
Generic extraction engine — reads persona config and applies rules.
Replaces hardcoded vp_pm_hybrid_themes.py with config-driven logic.
"""
from dataclasses import dataclass, field
from typing import Optional
from engine.config_loader import ConfigLoader


# Priority levels that qualify for strategic_only extraction
STRATEGIC_PRIORITIES = {'critical', 'high'}


@dataclass
class ExtractionResult:
    extract: bool
    reason: str
    project: Optional[str] = None
    matched_themes: list = field(default_factory=list)
    priority: str = "medium"


@dataclass
class NoiseFilterResult:
    """Result of noise filtering — determines if item passes through to AI triage."""
    pass_through: bool
    force_keep: bool = False
    reason: str = ""
    project: Optional[str] = None
    matched_themes: list = field(default_factory=list)
    priority: str = "medium"


class ExtractionEngine:
    """Config-driven extraction rules engine."""

    def __init__(self, config: ConfigLoader, custom_rules=None):
        self.config = config
        self.custom_rules = custom_rules

    def should_extract(
        self,
        text: str,
        author_username: str = "",
        channel_id: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Determine whether a message should be extracted as an action item.

        Evaluation order:
        1. Custom rules override (if custom_rules.py loaded)
        2. Always extract: user mentioned by name/alias/ID
        3. Always extract: from priority contact
        4. Always skip: matches skip_keywords
        5. Detect project -> apply extract_level + theme matching
        """
        text_lower = text.lower()

        # Detect project
        project = self.config.detect_project(text, channel_id)

        # 1. Custom rules override
        if self.custom_rules and hasattr(self.custom_rules, 'should_extract'):
            custom_result = self.custom_rules.should_extract(
                text, project, self._match_themes(text_lower), self.config.persona
            )
            if custom_result is not None:
                should, reason = custom_result
                return ExtractionResult(
                    extract=should, reason=reason, project=project
                )

        # 2. User mentioned
        if self.config.mentions_user(text):
            return ExtractionResult(
                extract=True,
                reason="User mentioned by name — always extract",
                project=project,
                priority="high"
            )

        # 3. Priority contact
        if self.config.is_priority_contact(author_username):
            return ExtractionResult(
                extract=True,
                reason="From priority contact — always extract",
                project=project,
                priority="high"
            )

        # 4. Skip keywords
        for kw in self.config.skip_keywords:
            if kw.lower() in text_lower:
                return ExtractionResult(
                    extract=False,
                    reason=f"Matches skip keyword: {kw}",
                    project=project
                )

        # 5. Theme matching + project extract_level
        matched = self._match_themes(text_lower)
        if not matched:
            return ExtractionResult(
                extract=False,
                reason="No theme match and no direct mention",
                project=project
            )

        # Get project extract level
        extract_level = "all"
        if project and project in self.config.projects:
            extract_level = self.config.projects[project].get("extract_level", "all")

        # Apply extract_level filter
        if extract_level == "all":
            best_priority = self._best_priority(matched)
            return ExtractionResult(
                extract=True,
                reason=f"Theme match for {extract_level} project: {', '.join(matched)}",
                project=project,
                matched_themes=matched,
                priority=best_priority
            )
        elif extract_level == "strategic_only":
            strategic_themes = [
                t for t in matched
                if self.config.themes.get(t, {}).get('priority', 'low') in STRATEGIC_PRIORITIES
            ]
            if strategic_themes:
                best_priority = self._best_priority(strategic_themes)
                return ExtractionResult(
                    extract=True,
                    reason=f"Strategic theme for {extract_level} project: {', '.join(strategic_themes)}",
                    project=project,
                    matched_themes=strategic_themes,
                    priority=best_priority
                )
            return ExtractionResult(
                extract=False,
                reason="Only low-priority themes for strategic_only project",
                project=project,
                matched_themes=matched
            )
        else:  # awareness_only
            return ExtractionResult(
                extract=False,
                reason="Awareness-only project — flagged but not extracted",
                project=project,
                matched_themes=matched
            )

    def noise_filter(
        self,
        text: str,
        author_username: str = "",
        channel_id: Optional[str] = None,
    ) -> NoiseFilterResult:
        """
        Lightweight noise filter for the two-step pipeline.

        Unlike should_extract() which makes a binary keep/skip decision,
        noise_filter() removes ONLY definitive noise and passes everything
        else through to AI triage. The AI handles semantic judgment.

        Removed (pass_through=False):
        - Messages matching skip_keywords
        - Very short messages (<10 chars, emoji-only)
        - Messages from awareness-only projects with no mention/priority signal

        Passed through with metadata:
        - Direct mentions -> force_keep=True
        - Priority contacts -> force_keep=True
        - Keyword-matched items -> tagged with matched_themes
        - Items with NO keyword match -> still passed through (AI decides)
        """
        text_lower = text.lower().strip()

        # Detect project
        project = self.config.detect_project(text, channel_id)

        # Very short / empty messages are noise
        if len(text_lower) < 10:
            return NoiseFilterResult(
                pass_through=False,
                reason="Too short (<10 chars)",
                project=project,
            )

        # Direct mentions -> force keep
        if self.config.mentions_user(text):
            matched = self._match_themes(text_lower)
            return NoiseFilterResult(
                pass_through=True,
                force_keep=True,
                reason="User mentioned by name",
                project=project,
                matched_themes=matched,
                priority="high",
            )

        # Priority contacts -> force keep
        if self.config.is_priority_contact(author_username):
            matched = self._match_themes(text_lower)
            return NoiseFilterResult(
                pass_through=True,
                force_keep=True,
                reason="From priority contact",
                project=project,
                matched_themes=matched,
                priority="high",
            )

        # Skip keywords -> definitive noise
        for kw in self.config.skip_keywords:
            if kw.lower() in text_lower:
                return NoiseFilterResult(
                    pass_through=False,
                    reason=f"Matches skip keyword: {kw}",
                    project=project,
                )

        # Awareness-only projects with no mention/priority -> noise
        if project and project in self.config.projects:
            extract_level = self.config.projects[project].get("extract_level", "all")
            if extract_level == "awareness_only":
                return NoiseFilterResult(
                    pass_through=False,
                    reason="Awareness-only project",
                    project=project,
                )

        # Everything else passes through — tag with any matched themes
        matched = self._match_themes(text_lower)
        best_priority = self._best_priority(matched) if matched else "medium"

        return NoiseFilterResult(
            pass_through=True,
            force_keep=False,
            reason="Candidate for AI triage" if not matched else f"Theme match: {', '.join(matched)}",
            project=project,
            matched_themes=matched,
            priority=best_priority,
        )

    def _match_themes(self, text_lower: str) -> list:
        """Return list of theme names whose keywords match the text."""
        matched = []
        for theme_name, theme_data in self.config.themes.items():
            for kw in theme_data.get('keywords', []):
                if kw.lower() in text_lower:
                    matched.append(theme_name)
                    break
        return matched

    def _best_priority(self, theme_names: list) -> str:
        """Return the highest priority among matched themes."""
        priority_rank = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        best = 'low'
        for name in theme_names:
            theme_priority = self.config.themes.get(name, {}).get('priority', 'low')
            if priority_rank.get(theme_priority, 3) < priority_rank.get(best, 3):
                best = theme_priority
        return best
