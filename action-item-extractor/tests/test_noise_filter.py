import pytest
import json
from pathlib import Path
from engine.config_loader import ConfigLoader
from engine.extraction_engine import ExtractionEngine, NoiseFilterResult
import yaml


def _make_engine(sample_persona, tmp_path):
    persona_file = tmp_path / "persona.yaml"
    persona_file.write_text(yaml.dump(sample_persona))
    loader = ConfigLoader(persona_path=str(persona_file))
    return ExtractionEngine(loader)


@pytest.fixture
def persona_with_awareness(sample_persona):
    """Persona with an awareness_only project."""
    persona = dict(sample_persona)
    persona['projects'] = dict(persona['projects'])
    persona['projects']['watch-only'] = {
        'name': 'Watch Only Project',
        'my_role': 'Observer',
        'extract_level': 'awareness_only',
        'detect_keywords': ['watch only'],
        'channels': ['C333333']
    }
    return persona


class TestNoiseFilter:
    """Test the noise_filter() method — lightweight pre-filter for AI triage."""

    def test_skip_keywords_removed(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="Fixed a typo in the documentation",
            author_username="random.person",
        )
        assert result.pass_through is False
        assert "skip keyword" in result.reason.lower()

    def test_short_messages_removed(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(text="ok", author_username="random.person")
        assert result.pass_through is False
        assert "short" in result.reason.lower()

    def test_empty_messages_removed(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(text="", author_username="random.person")
        assert result.pass_through is False

    def test_awareness_only_project_removed(self, persona_with_awareness, tmp_path):
        engine = _make_engine(persona_with_awareness, tmp_path)
        result = engine.noise_filter(
            text="Watch only project has a new update about the roadmap",
            author_username="random.person",
            channel_id="C333333",
        )
        assert result.pass_through is False
        assert "awareness" in result.reason.lower()

    def test_keyword_matched_items_tagged_not_removed(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="The team is blocked on the main product spec and needs a decision",
            author_username="random.person",
            channel_id="C111111",
        )
        assert result.pass_through is True
        assert result.force_keep is False
        assert len(result.matched_themes) > 0
        assert "blocking" in result.matched_themes

    def test_no_keyword_match_still_passes_through(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="Can someone review the deployment checklist before Friday?",
            author_username="random.person",
        )
        assert result.pass_through is True
        assert result.force_keep is False
        assert result.matched_themes == []
        assert "candidate" in result.reason.lower()

    def test_mentions_get_force_keep(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="Hey Test User, can you review this deployment?",
            author_username="random.person",
        )
        assert result.pass_through is True
        assert result.force_keep is True
        assert result.priority == "high"

    def test_priority_contact_gets_force_keep(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="Can someone look at the production issue?",
            author_username="boss.name",
        )
        assert result.pass_through is True
        assert result.force_keep is True
        assert result.priority == "high"

    def test_slack_user_id_mention_force_keep(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="<@U12345TEST> please review this PR",
            author_username="random.person",
        )
        assert result.pass_through is True
        assert result.force_keep is True

    def test_project_detected_in_result(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="The main product needs some attention this sprint",
            author_username="random.person",
            channel_id="C111111",
        )
        assert result.project == "main-product"

    def test_strategic_theme_gets_high_priority(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="We need to update the roadmap for Q3 prioritization",
            author_username="random.person",
        )
        assert result.pass_through is True
        assert result.priority == "high"
        assert "strategic" in result.matched_themes

    def test_critical_theme_gets_critical_priority(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        result = engine.noise_filter(
            text="The team is blocked and we have a blocker on the delivery",
            author_username="random.person",
        )
        assert result.pass_through is True
        assert result.priority == "critical"

    def test_multiple_skip_keywords_caught(self, sample_persona, tmp_path):
        engine = _make_engine(sample_persona, tmp_path)
        for kw in ["typo", "minor bug", "color change", "spacing"]:
            result = engine.noise_filter(
                text=f"Found a {kw} in the dashboard",
                author_username="random.person",
            )
            assert result.pass_through is False, f"Should filter out: {kw}"

    def test_existing_should_extract_unchanged(self, sample_persona, tmp_path):
        """Verify backward compat — should_extract() still works the same."""
        engine = _make_engine(sample_persona, tmp_path)

        # User mentioned — should extract
        result = engine.should_extract(
            text="Hey Test User, can you review this?",
            author_username="random.person",
        )
        assert result.extract is True
        assert "mentioned" in result.reason.lower()

        # No theme match — should skip
        result = engine.should_extract(
            text="The weather is nice today",
            author_username="random.person",
        )
        assert result.extract is False


class TestCollectAndFilter:
    """Test the Extractor.collect_and_filter() method."""

    def test_empty_sources_writes_empty_candidates(self, tmp_path, sample_persona, sample_config):
        """With no sources available, should write empty candidates file."""
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config = dict(sample_config)
        config['sources'] = {}  # No sources
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config))

        from engine.extractor import Extractor
        extractor = Extractor(
            persona_path=str(persona_file),
            config_path=str(config_file),
        )

        output_dir = tmp_path / "output"
        result = extractor.collect_and_filter(output_dir=str(output_dir))

        assert result['raw_items'] == 0
        assert result['after_noise_filter'] == 0
        assert (output_dir / 'candidates.json').exists()

        with open(output_dir / 'candidates.json') as f:
            payload = json.load(f)
        assert payload['candidates'] == []
        assert payload['stats']['raw_items'] == 0

    def test_candidates_json_has_persona(self, tmp_path, sample_persona, sample_config):
        """Candidates JSON should include persona data."""
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config = dict(sample_config)
        config['sources'] = {}
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config))

        from engine.extractor import Extractor
        extractor = Extractor(
            persona_path=str(persona_file),
            config_path=str(config_file),
        )

        output_dir = tmp_path / "output"
        extractor.collect_and_filter(output_dir=str(output_dir))

        with open(output_dir / 'candidates.json') as f:
            payload = json.load(f)

        assert 'persona' in payload
        assert payload['persona']['identity']['name'] == 'Test User'


class TestContentChunking:
    """Test the _chunk_item() method."""

    def test_short_content_not_chunked(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({'sources': {}}))

        from engine.extractor import Extractor
        extractor = Extractor(str(persona_file), str(config_file))

        item = {
            'content': 'Short message here',
            'author': 'test',
            'metadata': {'source_type': 'slack'}
        }
        chunks = extractor._chunk_item(item)
        assert len(chunks) == 1
        assert chunks[0]['content'] == 'Short message here'

    def test_gemini_notes_extracts_structured_sections(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({'sources': {}}))

        from engine.extractor import Extractor
        extractor = Extractor(str(persona_file), str(config_file))

        # Build realistic-length Gemini notes (>1500 chars to trigger chunking)
        transcript_lines = "\n".join([f"Alice: {'Discussion point about deployment details. ' * 5}" for _ in range(20)])
        content = f"""📝 Notes
Feb 19, 2026
DDS Delivery
Invited Alice Bob


Summary
The team discussed deployment plans and risk mitigation strategies for the upcoming release. Multiple concerns were raised about the database migration timeline and rollback procedures. The team aligned on a blue-green deployment pattern with automated rollback triggers.


Decisions
ALIGNED
* Deploy on Friday with rollback plan ready and automated triggers configured.
* Use blue-green deployment pattern with canary analysis before full cutover.

NEEDS FURTHER DISCUSSION
* Database migration rollback strategy needs more analysis before committing to Friday.


More details:
10:05 AM
Pratyush pushed back on adding actuals to the migration plan. He argued the rollback procedure already covers edge cases and adding actuals would slow the release by two days. Alice acknowledged the concern but noted that without actuals, the canary analysis would be less reliable. The team ultimately agreed to proceed without actuals but add a manual verification step.

10:15 AM
Massive latency issues raised with the super user approach to database access during migration. Bob demonstrated that queries through the super user account take 3x longer due to audit logging overhead. The team decided to create a dedicated migration service account with appropriate permissions instead. This requires a security review from the infrastructure team before Friday.


Suggested next steps
* Alice will prepare the rollback script by Thursday.
* Bob will run final integration tests Wednesday.
* Team lead will send go/no-go email Friday morning.


You should review Gemini's notes to make sure they're accurate.
📖 Transcript
Feb 19, 2026
00:00:00
{transcript_lines}
"""

        item = {
            'content': content,
            'author': 'Meeting Participants',
            'metadata': {'source_type': 'local_files', 'meeting_name': 'DDS Delivery'}
        }
        chunks = extractor._chunk_item(item)

        # Should produce ~4 chunks (next_steps, decisions, more_details, summary)
        assert len(chunks) <= 6, f"Expected <=6 structured chunks, got {len(chunks)}"
        assert len(chunks) >= 3, f"Expected >=3 chunks, got {len(chunks)}"

        # Next steps should be first chunk (highest value)
        assert 'next steps' in chunks[0]['content'].lower() or 'Suggested' in chunks[0]['content']
        assert 'Alice will prepare' in chunks[0]['content']
        assert chunks[0]['metadata']['section'] == 'next_steps'

        # More details section should be present with rich context
        more_details_chunks = [c for c in chunks if c.get('metadata', {}).get('section') == 'more_details']
        assert len(more_details_chunks) >= 1, "More details section should be extracted"
        all_details_text = ' '.join(c['content'] for c in more_details_chunks)
        assert 'Pratyush pushed back' in all_details_text
        assert 'latency issues' in all_details_text.lower()

        # Raw transcript content should NOT be in any chunk
        for chunk in chunks:
            assert '00:00:00' not in chunk['content']
            assert 'Discussion point about deployment details' not in chunk['content']

    def test_gemini_notes_drops_transcript_keeps_details(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({'sources': {}}))

        from engine.extractor import Extractor
        extractor = Extractor(str(persona_file), str(config_file))

        # Gemini note with large transcript AND more details
        transcript_lines = "\n".join([f"Speaker {i}: " + "x" * 200 for i in range(50)])
        content = f"""📝 Notes
Feb 19, 2026
Big Meeting


Summary
Important decisions were made about the product roadmap and resource allocation.


More details:
09:30 AM
The VP pushed back on the timeline for the API redesign. She noted that the current architecture handles 95% of use cases and the remaining 5% could be addressed with targeted patches rather than a full rewrite.

09:45 AM
Engineering lead demonstrated that the performance bottleneck is in the caching layer, not the API layer. Team agreed to focus optimization efforts on cache invalidation before considering any API changes.


Suggested next steps
* Do the thing by Friday.
* Review caching strategy by next sprint.


📖 Transcript
{transcript_lines}
"""
        item = {
            'content': content,
            'author': 'Test',
            'metadata': {'source_type': 'local_files', 'meeting_name': 'Big Meeting'}
        }
        chunks = extractor._chunk_item(item)
        total_chars = sum(len(c['content']) for c in chunks)
        # Should be dramatically smaller than the full content (transcript dropped)
        assert total_chars < len(content) / 2, f"Chunks ({total_chars} chars) should be much smaller than full content ({len(content)} chars)"

        # More details context should be preserved
        all_text = ' '.join(c['content'] for c in chunks)
        assert 'VP pushed back' in all_text
        assert 'caching layer' in all_text

        # Raw transcript should NOT be present
        assert 'xxxx' not in all_text

    def test_non_gemini_transcript_uses_paragraph_chunking(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({'sources': {}}))

        from engine.extractor import Extractor
        extractor = Extractor(str(persona_file), str(config_file))

        # Non-Gemini long content (no 📝 Notes marker)
        content = "\n\n".join([f"Speaker {i}: This is a paragraph of content that represents a speaker turn." + " Extra content." * 20 for i in range(20)])

        item = {
            'content': content,
            'author': 'Meeting Participants',
            'metadata': {'source_type': 'local_files', 'meeting_name': 'Test Meeting'}
        }
        chunks = extractor._chunk_item(item)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk['metadata']['is_chunk'] is True

    def test_chunk_preserves_metadata(self, tmp_path, sample_persona):
        persona_file = tmp_path / "persona.yaml"
        persona_file.write_text(yaml.dump(sample_persona))
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({'sources': {}}))

        from engine.extractor import Extractor
        extractor = Extractor(str(persona_file), str(config_file))

        content = "\n\n".join(["Paragraph " + "x" * 1500 for _ in range(5)])
        item = {
            'content': content,
            'author': 'Test Author',
            'timestamp': '2026-02-20T10:00:00',
            'url': 'https://example.com',
            'metadata': {
                'source_type': 'local_files',
                'meeting_name': 'Test Meeting',
                'file_name': 'test.txt'
            }
        }
        chunks = extractor._chunk_item(item)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk['author'] == 'Test Author'
            assert chunk['metadata']['source_type'] == 'local_files'
            assert chunk['metadata']['meeting_name'] == 'Test Meeting'
