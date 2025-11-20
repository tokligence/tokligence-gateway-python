"""
Tests for chat knowledge base module
"""

import pytest
from pathlib import Path
from tokligence.chat.knowledge import KnowledgeBase, load_knowledge


def test_knowledge_base_init():
    """Test KnowledgeBase initialization"""
    kb = KnowledgeBase()
    assert kb.meta == {}
    assert kb.docs == {}
    assert 'github' in kb.links
    assert 'pypi' in kb.links


def test_knowledge_base_load():
    """Test loading knowledge base"""
    kb = load_knowledge()

    # Should have loaded docs
    assert isinstance(kb.docs, dict)

    # Check for expected docs (these were synced)
    expected_docs = ['README', 'QUICK_START', 'USER_GUIDE', 'configuration_guide']
    for doc in expected_docs:
        assert doc in kb.docs, f"Expected doc '{doc}' not found in knowledge base"


def test_get_doc():
    """Test getting specific document"""
    kb = load_knowledge()

    # Get README
    readme = kb.get_doc('README')
    assert readme is not None
    assert isinstance(readme, str)
    assert len(readme) > 0

    # Get non-existent doc
    nonexistent = kb.get_doc('NONEXISTENT')
    assert nonexistent is None


def test_search_docs():
    """Test searching documentation"""
    kb = load_knowledge()

    # Search for common term
    results = kb.search_docs('OpenAI')
    assert isinstance(results, list)

    # Each result should have required fields
    for result in results:
        assert 'doc' in result
        assert 'section' in result
        assert 'line' in result
        assert 'content' in result


def test_search_docs_no_results():
    """Test searching for term that doesn't exist"""
    kb = load_knowledge()

    results = kb.search_docs('XYZABC123NOTFOUND')
    assert results == []


def test_build_system_prompt():
    """Test system prompt generation"""
    kb = load_knowledge()

    prompt = kb.build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0

    # Should mention Tokligence Gateway
    assert 'Tokligence Gateway' in prompt

    # Should mention available tools
    assert 'set_config' in prompt
    assert 'get_config' in prompt
    assert 'search_docs' in prompt


def test_get_available_docs():
    """Test getting list of available docs"""
    kb = load_knowledge()

    docs = kb.get_available_docs()
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert 'README' in docs
