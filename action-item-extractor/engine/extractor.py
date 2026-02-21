"""
Main extractor orchestrator — ties together sources, engine, and outputs.
Loads plugins by type from config.
"""
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from engine.config_loader import ConfigLoader
from engine.extraction_engine import ExtractionEngine
from engine.dedup import Deduplicator


# Approximate chars per token for budget estimation
CHARS_PER_TOKEN = 4
# Max tokens for a single Claude Code triage batch
MAX_BATCH_TOKENS = 150_000


class Extractor:
    """Main orchestrator that loads sources/outputs by type and runs extraction."""

    # Plugin registries — maps type string to (module_path, class_name)
    SOURCE_REGISTRY = {
        'local_files': ('sources.local_files_source', 'LocalFilesSource'),
        'slack': ('sources.slack_source', 'SlackSource'),
        'jira': ('sources.jira_source', 'JiraSource'),
        'confluence': ('sources.confluence_source', 'ConfluenceSource'),
        'email': ('sources.email_source', 'EmailSource'),
        'google_sheets': ('sources.google_sheets_source', 'GoogleSheetsSource'),
        'google_docs': ('sources.google_docs_source', 'GoogleDocsSource'),
    }

    OUTPUT_REGISTRY = {
        'obsidian': ('outputs.obsidian_output', 'ObsidianOutput'),
        'markdown': ('outputs.markdown_output', 'MarkdownOutput'),
        'csv': ('outputs.csv_output', 'CsvOutput'),
    }

    def __init__(self, persona_path: str, config_path: str):
        self.logger = logging.getLogger('Extractor')

        # Load config
        self.config_loader = ConfigLoader(persona_path=persona_path, config_path=config_path)
        self.persona = self.config_loader.persona
        self.config = self.config_loader.config

        # Initialize engine
        self.engine = ExtractionEngine(self.config_loader)
        self.dedup = Deduplicator()

        # Load source plugins
        self.sources = self._load_sources()

        # Load output plugin
        self.output = self._load_output()

        # AI processor (lazy — only init when needed)
        self._ai_processor = None

    def _load_sources(self) -> list:
        """Load enabled source plugins based on config."""
        sources = []
        for name, source_config in self.config.get('sources', {}).items():
            if not source_config.get('enabled', False):
                continue

            source_type = source_config.get('type', '')
            if source_type not in self.SOURCE_REGISTRY:
                self.logger.warning(f"Unknown source type: {source_type}")
                continue

            module_path, class_name = self.SOURCE_REGISTRY[source_type]
            try:
                import importlib
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                # Inject shared Google config for Google-based sources
                if source_type in ('google_sheets', 'google_docs', 'email'):
                    google_config = self.config.get('google', {})
                    if google_config:
                        source_config = dict(source_config)
                        source_config['_google_config'] = google_config
                source = cls(source_config, self.persona)
                if source.is_available():
                    sources.append(source)
                    self.logger.info(f"Loaded source: {name} ({source_type})")
                else:
                    self.logger.warning(f"Source not available: {name} ({source_type})")
            except Exception as e:
                self.logger.error(f"Failed to load source {name}: {e}")

        return sources

    def _load_output(self):
        """Load output plugin based on config."""
        output_config = self.config.get('output', {})
        output_type = output_config.get('type', 'markdown')

        if output_type not in self.OUTPUT_REGISTRY:
            self.logger.warning(f"Unknown output type: {output_type}, falling back to markdown")
            output_type = 'markdown'

        module_path, class_name = self.OUTPUT_REGISTRY[output_type]
        try:
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls(output_config, self.persona)
        except Exception as e:
            self.logger.error(f"Failed to load output {output_type}: {e}")
            return None

    def collect_raw_items(self) -> List[Dict]:
        """Collect raw items from all enabled sources."""
        all_items = []
        for source in self.sources:
            try:
                items = source.extract()
                self.logger.info(f"{type(source).__name__}: extracted {len(items)} items")
                all_items.extend(items)
            except Exception as e:
                self.logger.error(f"Error extracting from {type(source).__name__}: {e}")
        return all_items

    def collect_and_filter(self, output_dir: str = '/tmp/action-item-candidates') -> dict:
        """
        Step 1 of two-step pipeline: collect from all sources + noise filter.

        Writes candidates JSON to output_dir. If content exceeds token budget,
        splits into multiple batch files.

        Returns dict with stats about the collection.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Collect raw items from all sources
        raw_items = self.collect_raw_items()
        self.logger.info(f"Collected {len(raw_items)} raw items from {len(self.sources)} sources")

        if not raw_items:
            # Write empty candidates file
            result = self._build_candidates_payload([], 0)
            self._write_candidates(out_path / 'candidates.json', result)
            return {'raw_items': 0, 'after_noise_filter': 0, 'batch_files': 1}

        # 2. Chunk long content (meeting transcripts, long emails)
        chunked_items = []
        for item in raw_items:
            chunks = self._chunk_item(item)
            chunked_items.extend(chunks)
        self.logger.info(f"After chunking: {len(chunked_items)} items (from {len(raw_items)} raw)")

        # 3. Apply noise filter
        candidates = []
        for item in chunked_items:
            result = self.engine.noise_filter(
                text=item.get('content', ''),
                author_username=item.get('author', ''),
                channel_id=item.get('metadata', {}).get('channel_id'),
            )
            if result.pass_through:
                candidate = self._item_to_candidate(item, result)
                candidates.append(candidate)

        self.logger.info(f"After noise filter: {len(candidates)} candidates (from {len(chunked_items)} chunked)")

        # 4. Check token budget and split into batches if needed
        batches = self._split_into_batches(candidates)
        self.logger.info(f"Split into {len(batches)} batch(es)")

        # 5. Write batch files
        batch_files = []
        if len(batches) == 1:
            filename = 'candidates.json'
            payload = self._build_candidates_payload(batches[0], len(raw_items))
            self._write_candidates(out_path / filename, payload)
            batch_files.append(str(out_path / filename))
        else:
            for i, batch in enumerate(batches, 1):
                filename = f'candidates_batch_{i}.json'
                payload = self._build_candidates_payload(batch, len(raw_items), batch_num=i, total_batches=len(batches))
                self._write_candidates(out_path / filename, payload)
                batch_files.append(str(out_path / filename))

        return {
            'raw_items': len(raw_items),
            'after_chunking': len(chunked_items),
            'after_noise_filter': len(candidates),
            'batch_files': len(batches),
            'output_files': batch_files,
        }

    # Gemini note section markers
    _GEMINI_HEADER = '📝 Notes'
    _GEMINI_TRANSCRIPT_MARKER = '📖 Transcript'
    _GEMINI_SECTIONS = re.compile(
        r'^(Summary|Details|Decisions|Suggested next steps|More details:)',
        re.MULTILINE
    )
    _GEMINI_BOILERPLATE = re.compile(
        r"You should review Gemini's notes.*$|Please provide feedback.*$",
        re.MULTILINE
    )

    def _chunk_item(self, item: dict) -> List[Dict]:
        """
        Split long content into smaller chunks for AI processing.

        Gemini meeting notes: extract only structured sections (summary, decisions,
        next steps). Drop the raw transcript — Gemini already summarized it.
        Other long content: split by paragraphs at ~3000 char boundaries.
        Short items (<1500 chars): pass through unchanged.
        """
        content = item.get('content', '')
        source_type = item.get('metadata', {}).get('source_type', '')

        # Short content — pass through as-is
        if len(content) <= 1500:
            return [item]

        # Meeting transcripts — detect Gemini format or fall back
        if source_type == 'local_files':
            if self._GEMINI_HEADER in content:
                return self._chunk_gemini_notes(item, content)
            return self._chunk_by_paragraphs(item, content)

        # Other long content — split by paragraphs
        return self._chunk_by_paragraphs(item, content)

    def _chunk_gemini_notes(self, item: dict, content: str) -> List[Dict]:
        """
        Parse Gemini meeting notes and extract structured sections with context.

        Gemini notes structure:
          📝 Notes / Header / Attendees
          Summary (topic paragraphs)
          Details > Decisions (ALIGNED, NEEDS FURTHER DISCUSSION)
          Details > More details (timestamped context paragraphs — rich detail)
          Suggested next steps (bullet points)
          [boilerplate]
          📖 Transcript (raw speaker turns — DROPPED)

        We keep: summary + decisions + more details + next steps.
        We drop: ONLY the raw 📖 Transcript (speaker turns with filler words)
                 and Gemini boilerplate.
        The "More details" section contains rich contextual paragraphs that
        provide essential context for action items (e.g., who pushed back,
        what concerns were raised, what latency issues exist).
        """
        # Strip the raw transcript (everything after 📖 Transcript)
        transcript_idx = content.find(self._GEMINI_TRANSCRIPT_MARKER)
        if transcript_idx > 0:
            content = content[:transcript_idx]

        # Strip boilerplate
        content = self._GEMINI_BOILERPLATE.sub('', content).strip()

        # Extract meeting name from metadata or first lines
        meeting_name = item.get('metadata', {}).get('meeting_name', '')

        chunks = []

        # Find "Suggested next steps" section — highest value for action items
        next_steps = self._extract_section(content, 'Suggested next steps')
        if next_steps:
            header = f"Meeting: {meeting_name}\n\n" if meeting_name else ""
            chunk_content = f"{header}Suggested next steps:\n{next_steps}"
            chunk = self._make_chunk(item, chunk_content, len(chunks))
            chunk['metadata']['section'] = 'next_steps'
            chunks.append(chunk)

        # Find "Decisions" section — second highest value
        decisions = self._extract_section(content, 'Decisions')
        if decisions:
            header = f"Meeting: {meeting_name}\n\n" if meeting_name else ""
            chunk_content = f"{header}Decisions:\n{decisions}"
            chunk = self._make_chunk(item, chunk_content, len(chunks))
            chunk['metadata']['section'] = 'decisions'
            chunks.append(chunk)

        # "More details" — rich contextual paragraphs with timestamps.
        # These provide the context that makes action items useful
        # (e.g., "Pratyush pushed back on adding actuals", "Massive latency issues")
        more_details = self._extract_section(content, 'More details')
        if more_details and len(more_details) > 50:
            header = f"Meeting: {meeting_name}\n\n" if meeting_name else ""
            # More details can be long — chunk at ~3000 char boundaries
            if len(more_details) > 3000:
                detail_paragraphs = re.split(r'\n\s*\n', more_details)
                current_detail = ""
                for para in detail_paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    if len(current_detail) + len(para) > 3000 and current_detail:
                        chunk_content = f"{header}More details:\n{current_detail}"
                        chunk = self._make_chunk(item, chunk_content, len(chunks))
                        chunk['metadata']['section'] = 'more_details'
                        chunks.append(chunk)
                        current_detail = para
                    else:
                        current_detail = f"{current_detail}\n\n{para}" if current_detail else para
                if current_detail.strip():
                    chunk_content = f"{header}More details:\n{current_detail}"
                    chunk = self._make_chunk(item, chunk_content, len(chunks))
                    chunk['metadata']['section'] = 'more_details'
                    chunks.append(chunk)
            else:
                chunk_content = f"{header}More details:\n{more_details}"
                chunk = self._make_chunk(item, chunk_content, len(chunks))
                chunk['metadata']['section'] = 'more_details'
                chunks.append(chunk)

        # Summary — provides high-level context
        summary = self._extract_section(content, 'Summary')
        if summary and len(summary) > 50:
            header = f"Meeting: {meeting_name}\n\n" if meeting_name else ""
            chunk_content = f"{header}Summary:\n{summary}"
            chunk = self._make_chunk(item, chunk_content, len(chunks))
            chunk['metadata']['section'] = 'summary'
            chunks.append(chunk)

        # If we extracted structured sections, use them
        if chunks:
            return chunks

        # Fallback: not a well-structured Gemini note — use paragraph chunking
        return self._chunk_by_paragraphs(item, content)

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract text between a section header and the next section header."""
        # Find the section start
        pattern = re.compile(rf'^{re.escape(section_name)}\s*$', re.MULTILINE)
        match = pattern.search(content)
        if not match:
            # Try with colon variant (e.g., "More details:")
            pattern = re.compile(rf'^{re.escape(section_name)}:?\s*$', re.MULTILINE)
            match = pattern.search(content)
        if not match:
            return None

        start = match.end()

        # Find the next section header or end of content
        next_section = self._GEMINI_SECTIONS.search(content, start)
        if next_section:
            end = next_section.start()
        else:
            end = len(content)

        section_text = content[start:end].strip()
        # Strip "Rate these decisions" boilerplate from Decisions section
        section_text = re.sub(r'Rate these decisions:.*$', '', section_text, flags=re.MULTILINE).strip()
        return section_text if section_text else None

    def _chunk_by_paragraphs(self, item: dict, content: str) -> List[Dict]:
        """Split content by paragraph breaks, targeting ~3000 char chunks."""
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) > 3000 and current_chunk:
                chunks.append(self._make_chunk(item, current_chunk, len(chunks)))
                current_chunk = para
            else:
                current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para

        if current_chunk.strip():
            chunks.append(self._make_chunk(item, current_chunk, len(chunks)))

        return chunks if chunks else [item]

    def _make_chunk(self, item: dict, chunk_content: str, chunk_index: int) -> dict:
        """Create a new item dict for a content chunk, preserving metadata."""
        chunk = dict(item)
        chunk['content'] = chunk_content.strip()
        chunk['metadata'] = dict(item.get('metadata', {}))
        chunk['metadata']['chunk_index'] = chunk_index
        chunk['metadata']['is_chunk'] = True
        return chunk

    def _item_to_candidate(self, item: dict, filter_result) -> dict:
        """Convert a raw item + noise filter result into a candidate dict for JSON output."""
        return {
            'content': item.get('content', ''),
            'author': item.get('author', ''),
            'timestamp': str(item.get('timestamp', '')),
            'source_type': item.get('metadata', {}).get('source_type', 'unknown'),
            'source_url': item.get('url', ''),
            'metadata': {
                'channel_name': item.get('metadata', {}).get('channel_name', ''),
                'channel_id': item.get('metadata', {}).get('channel_id', ''),
                'meeting_name': item.get('metadata', {}).get('meeting_name', ''),
                'file_name': item.get('metadata', {}).get('file_name', ''),
                'is_chunk': item.get('metadata', {}).get('is_chunk', False),
                'chunk_index': item.get('metadata', {}).get('chunk_index', 0),
                'force_keep': filter_result.force_keep,
                'matched_themes': filter_result.matched_themes,
                'filter_reason': filter_result.reason,
                'project': filter_result.project,
                'priority': filter_result.priority,
            }
        }

    def _split_into_batches(self, candidates: list) -> List[List[dict]]:
        """Split candidates into batches that fit within the token budget."""
        if not candidates:
            return [[]]

        # Estimate persona context overhead (~10K tokens)
        persona_overhead = 10_000
        available_tokens = MAX_BATCH_TOKENS - persona_overhead

        batches = [[]]
        current_tokens = 0

        for candidate in candidates:
            # Estimate tokens for this candidate
            candidate_chars = len(json.dumps(candidate, default=str))
            candidate_tokens = candidate_chars // CHARS_PER_TOKEN

            if current_tokens + candidate_tokens > available_tokens and batches[-1]:
                batches.append([])
                current_tokens = 0

            batches[-1].append(candidate)
            current_tokens += candidate_tokens

        return batches

    def _build_candidates_payload(self, candidates: list, raw_count: int,
                                   batch_num: int = 1, total_batches: int = 1) -> dict:
        """Build the JSON payload for Claude Code triage."""
        return {
            'persona': self.persona,
            'output': self.config.get('output', {}),
            'candidates': candidates,
            'stats': {
                'raw_items': raw_count,
                'after_noise_filter': len(candidates),
                'batch': batch_num,
                'total_batches': total_batches,
            }
        }

    @staticmethod
    def _write_candidates(path: Path, payload: dict):
        """Write candidates payload to JSON file."""
        with open(path, 'w') as f:
            json.dump(payload, f, default=str, indent=2)

    def run(self) -> Dict:
        """Run full extraction pipeline: collect -> filter -> dedup -> AI -> save."""
        # 1. Collect raw items from all sources
        raw_items = self.collect_raw_items()
        self.logger.info(f"Collected {len(raw_items)} raw items from {len(self.sources)} sources")

        if not raw_items:
            return {'raw_items': 0, 'extracted': 0, 'saved': 0}

        # 2. Filter through extraction engine
        filtered = []
        for item in raw_items:
            result = self.engine.should_extract(
                text=item.get('content', ''),
                author_username=item.get('author', ''),
                channel_id=item.get('metadata', {}).get('channel_id')
            )
            if result.extract:
                item['_extraction_result'] = {
                    'reason': result.reason,
                    'project': result.project,
                    'themes': result.matched_themes,
                    'priority': result.priority
                }
                filtered.append(item)

        self.logger.info(f"Filtered to {len(filtered)} items")

        # 3. Process with AI (if available)
        if self._get_ai_processor():
            action_items = self._ai_processor.extract_action_items(filtered)
        else:
            # Fallback: use extraction result as basic task
            action_items = self._items_to_basic_tasks(filtered)

        # 4. Deduplicate
        action_items = self.dedup.deduplicate(action_items)
        self.logger.info(f"After dedup: {len(action_items)} tasks")

        # 5. Save to output
        if self.output and action_items:
            self.output.save_tasks(action_items)
            self.logger.info(f"Saved {len(action_items)} tasks")

        return {
            'raw_items': len(raw_items),
            'extracted': len(filtered),
            'saved': len(action_items)
        }

    def _get_ai_processor(self):
        """Lazy-init AI processor."""
        if self._ai_processor is None:
            ai_config = self.config.get('ai', {})
            if ai_config.get('api_key'):
                try:
                    from engine.ai_processor import AIProcessor
                    self._ai_processor = AIProcessor(ai_config, self.persona)
                except Exception as e:
                    self.logger.warning(f"AI processor not available: {e}")
        return self._ai_processor

    def _items_to_basic_tasks(self, items: List[Dict]) -> List[Dict]:
        """Convert raw items to basic task format (no AI enrichment)."""
        tasks = []
        for item in items:
            extraction = item.get('_extraction_result', {})
            tasks.append({
                'title': item.get('content', '')[:100],
                'requestor': item.get('author', 'Unknown'),
                'context': item.get('content', '')[:500],
                'due_date': None,
                'priority': extraction.get('priority', 'medium'),
                'project': extraction.get('project', ''),
                'source_url': item.get('url', ''),
                'source_author': item.get('author', ''),
                'source_type': item.get('metadata', {}).get('source_type', 'unknown'),
                'source_timestamp': str(item.get('timestamp', '')),
                'confidence': 1.0
            })
        return tasks
