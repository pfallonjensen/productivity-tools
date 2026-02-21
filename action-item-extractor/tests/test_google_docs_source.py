import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sources.google_docs_source import GoogleDocsSource


@pytest.fixture
def docs_config():
    return {
        'type': 'google_docs',
        'document_id': 'test-doc-id',
        'tab': 'latest',
        'lookback_hours': 168,
        'section_delimiter': '---',
        '_google_config': {
            'credentials_path': '/tmp/test-creds.json',
            'client_id': 'test-id',
            'client_secret': 'test-secret',
            'scopes': ['https://www.googleapis.com/auth/documents.readonly'],
        }
    }


class TestGoogleDocsSource:
    def test_is_available_no_document_id(self, sample_persona):
        config = {'type': 'google_docs', 'document_id': ''}
        source = GoogleDocsSource(config, sample_persona)
        assert source.is_available() is False

    def test_is_available_no_auth(self, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)
        with patch.object(source, '_get_auth_manager') as mock_auth:
            mock_auth.return_value.is_authenticated.return_value = False
            assert source.is_available() is False

    def test_extract_returns_empty_when_unavailable(self, sample_persona):
        config = {'type': 'google_docs', 'document_id': ''}
        source = GoogleDocsSource(config, sample_persona)
        assert source.extract() == []

    @patch('sources.google_docs_source.GoogleDocsSource._get_auth_manager')
    @patch('sources.google_docs_source.GoogleDocsSource._get_modification_time')
    def test_extract_parses_document(self, mock_mod_time, mock_auth_method, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)
        mock_mod_time.return_value = datetime.now()

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_service.documents.return_value.get.return_value.execute.return_value = {
            'title': 'Test Document',
            'body': {
                'content': [
                    {
                        'paragraph': {
                            'elements': [
                                {'textRun': {'content': 'Section one content here. '}}
                            ]
                        }
                    },
                    {
                        'paragraph': {
                            'elements': [
                                {'textRun': {'content': '---'}}
                            ]
                        }
                    },
                    {
                        'paragraph': {
                            'elements': [
                                {'textRun': {'content': 'Section two with more content that is long enough. '}}
                            ]
                        }
                    }
                ]
            }
        }

        items = source.extract()
        assert len(items) >= 1
        assert items[0]['metadata']['source_type'] == 'google_docs'
        assert items[0]['metadata']['document_title'] == 'Test Document'

    def test_extract_text_from_body(self, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)

        body = {
            'content': [
                {
                    'paragraph': {
                        'elements': [
                            {'textRun': {'content': 'Hello '}},
                            {'textRun': {'content': 'World'}},
                        ]
                    }
                }
            ]
        }

        text = source._extract_text(body)
        assert 'Hello' in text
        assert 'World' in text

    def test_extract_text_from_table(self, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)

        body = {
            'content': [
                {
                    'table': {
                        'tableRows': [
                            {
                                'tableCells': [
                                    {
                                        'content': [
                                            {
                                                'paragraph': {
                                                    'elements': [
                                                        {'textRun': {'content': 'Cell content'}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

        text = source._extract_text(body)
        assert 'Cell content' in text

    def test_split_into_sections_with_delimiter(self, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)

        content = "Section one with enough content here.\n---\nSection two also has sufficient content.\n---\nSection three completes the document."
        sections = source._split_into_sections(content)
        assert len(sections) == 3

    def test_split_into_sections_fallback_paragraphs(self, sample_persona, docs_config):
        docs_config['section_delimiter'] = ''
        source = GoogleDocsSource(docs_config, sample_persona)

        content = "Paragraph one with lots of content.\n\n" * 10
        sections = source._split_into_sections(content)
        assert len(sections) >= 1

    @patch('sources.google_docs_source.GoogleDocsSource._get_auth_manager')
    @patch('sources.google_docs_source.GoogleDocsSource._get_modification_time')
    def test_extract_empty_document(self, mock_mod_time, mock_auth_method, sample_persona, docs_config):
        source = GoogleDocsSource(docs_config, sample_persona)
        mock_mod_time.return_value = datetime.now()

        mock_service = MagicMock()
        mock_auth_method.return_value.get_service.return_value = mock_service
        mock_auth_method.return_value.is_authenticated.return_value = True

        mock_service.documents.return_value.get.return_value.execute.return_value = {
            'title': 'Empty Doc',
            'body': {'content': []}
        }

        items = source.extract()
        assert items == []
