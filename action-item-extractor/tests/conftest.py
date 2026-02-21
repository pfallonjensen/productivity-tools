import pytest
import yaml
from pathlib import Path


@pytest.fixture
def sample_persona():
    """Minimal persona config for testing"""
    return {
        'identity': {
            'name': 'Test User',
            'aliases': ['Test', 'TU', 'test.user'],
            'slack_user_id': 'U12345TEST',
            'role': 'Product Manager'
        },
        'projects': {
            'main-product': {
                'name': 'Main Product',
                'my_role': 'PM and owner',
                'extract_level': 'all',
                'detect_keywords': ['main product', 'MP'],
                'channels': ['C111111']
            },
            'side-project': {
                'name': 'Side Project',
                'my_role': 'Executive oversight',
                'extract_level': 'strategic_only',
                'detect_keywords': ['side project'],
                'channels': ['C222222']
            }
        },
        'priority_contacts': [
            {'username': 'boss.name', 'reason': 'CEO'},
            {'username': 'key.person', 'reason': 'Key stakeholder'}
        ],
        'themes': {
            'blocking': {
                'priority': 'critical',
                'description': 'Team blocked',
                'keywords': ['blocked', 'need decision', 'blocker', 'waiting on']
            },
            'strategic': {
                'priority': 'high',
                'description': 'Direction decisions',
                'keywords': ['roadmap', 'strategy', 'prioritize', 'go-live']
            },
            'customer_critical': {
                'priority': 'high',
                'description': 'Customer issues',
                'keywords': ['escalation', 'churn risk', 'customer requirement']
            },
            'awareness': {
                'priority': 'low',
                'description': 'FYI items',
                'keywords': ['fyi', 'status update', 'heads up']
            }
        },
        'skip_keywords': ['typo', 'minor bug', 'color change', 'spacing'],
        'ticket_detection': {
            'enabled': True,
            'pattern': r'[A-Z]{2,5}-\d{1,5}'
        }
    }


@pytest.fixture
def sample_config():
    """Minimal config for testing"""
    return {
        'sources': {
            'slack': {
                'enabled': True,
                'type': 'slack',
                'token': 'xoxp-test-token',
                'lookback_hours': 24
            },
            'meetings': {
                'enabled': True,
                'type': 'local_files',
                'path': '/tmp/test-transcripts',
                'file_patterns': ['*.txt', '*.md'],
                'lookback_hours': 48
            }
        },
        'output': {
            'type': 'obsidian',
            'path': '/tmp/test-vault',
            'action_items_path': 'Action Items',
            'preserve_manual_priorities': True,
            'carry_forward_incomplete': True,
            'past_due_tracking': True
        },
        'ai': {
            'provider': 'anthropic',
            'api_key': 'test-key',
            'model': 'claude-sonnet-4-5-20250929',
            'confidence_threshold': 0.7
        },
        'schedule': {
            'times': ['06:00', '11:00', '15:00', '18:00'],
            'log_file': 'extract-tasks.log',
            'max_log_size_mb': 10
        }
    }


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary Obsidian vault structure for testing"""
    action_items = tmp_path / "Action Items"
    action_items.mkdir()
    (action_items / "By Source").mkdir()
    (action_items / "By Source" / "From Meetings").mkdir()
    (action_items / "By Source" / "From Slack").mkdir()
    return tmp_path
