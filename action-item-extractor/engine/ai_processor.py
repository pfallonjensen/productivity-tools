"""
AI processor — uses Claude API to extract action items from raw content.
Config-driven: model, API key, confidence threshold from config.yaml.
User identity from persona.yaml.
"""
import json
import logging
import anthropic
from typing import List, Dict


class AIProcessor:
    """Process content with Claude AI to extract action items."""

    def __init__(self, ai_config: dict, persona: dict):
        self.config = ai_config
        self.persona = persona
        self.api_key = ai_config.get('api_key', '')
        self.model = ai_config.get('model', 'claude-sonnet-4-5-20250929')
        self.confidence_threshold = ai_config.get('confidence_threshold', 0.7)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logging.getLogger('AIProcessor')

        # Extract identity from persona
        identity = persona.get('identity', {})
        self.user_name = identity.get('name', '')
        self.user_aliases = identity.get('aliases', [])
        self.role = identity.get('role', '')

    def extract_action_items(self, items: List[Dict]) -> List[Dict]:
        """Extract action items from raw content using Claude AI."""
        action_items = []

        for item in items:
            try:
                prompt = self._build_extraction_prompt(item)

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )

                result_text = response.content[0].text
                extracted = self._parse_response(result_text)

                # Add source metadata
                for task in extracted:
                    task['source_url'] = item.get('url', '')
                    task['source_timestamp'] = str(item.get('timestamp', ''))
                    task['source_author'] = item.get('author', '')
                    task['source_type'] = item.get('source_type', item.get('metadata', {}).get('source_type', 'unknown'))
                    task['source_metadata'] = item.get('metadata', {})

                action_items.extend(extracted)

            except Exception as e:
                self.logger.error(f"Error processing item with AI: {e}")

        return action_items

    def _build_extraction_prompt(self, item: Dict) -> str:
        """Build prompt using persona identity."""
        aliases_str = ', '.join(f'"{a}"' for a in self.user_aliases)

        return f"""You are an AI assistant extracting action items for {self.user_name} ({self.role}).
Also known as: {aliases_str}.

Analyze the following content and extract ALL action items for {self.user_name}.

SOURCE TYPE: {item.get('source_type', 'unknown')}
AUTHOR: {item.get('author', 'unknown')}
TIMESTAMP: {item.get('timestamp', 'unknown')}

CONTENT:
{item.get('content', '')}

INSTRUCTIONS:
1. Extract ONLY items that {self.user_name} committed to or was asked to do
2. For each item identify: title, requestor, context, due_date, priority, project, confidence
3. Be specific — include enough context to understand the task
4. Skip general discussion, FYI items, or already-completed items

Return a JSON array:
```json
[
  {{
    "title": "Clear actionable description",
    "requestor": "Person who made the request",
    "context": "Brief context",
    "due_date": "YYYY-MM-DD or null",
    "priority": "high" | "medium" | "low",
    "project": "Project name",
    "confidence": 0.0-1.0
  }}
]
```

If NO action items, return: []
Only extract items with confidence >= {self.confidence_threshold}"""

    def _parse_response(self, response_text: str) -> List[Dict]:
        """Parse JSON response, filter by confidence threshold."""
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1

            if start == -1 or end == 0:
                return []

            json_str = response_text[start:end]
            tasks = json.loads(json_str)

            return [t for t in tasks if t.get('confidence', 0) >= self.confidence_threshold]

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return []
