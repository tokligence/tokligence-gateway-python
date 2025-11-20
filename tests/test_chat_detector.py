"""
Tests for chat LLM detector module
"""

import pytest
import os
from tokligence.chat.detector import LLMDetector, Endpoint, select_endpoint


@pytest.mark.asyncio
async def test_detector_init():
    """Test LLMDetector initialization"""
    detector = LLMDetector()
    assert detector.endpoints == []


@pytest.mark.asyncio
async def test_detect_openai_with_key():
    """Test OpenAI detection when API key is present"""
    # Set test API key
    os.environ['TOKLIGENCE_OPENAI_API_KEY'] = 'sk-test123'

    detector = LLMDetector()
    await detector._detect_openai()

    assert len(detector.endpoints) == 1
    endpoint = detector.endpoints[0]
    assert endpoint.type == 'openai'
    assert endpoint.name == 'OpenAI API'
    assert endpoint.available
    assert not endpoint.local

    # Cleanup
    del os.environ['TOKLIGENCE_OPENAI_API_KEY']


@pytest.mark.asyncio
async def test_detect_openai_without_key():
    """Test OpenAI detection when API key is not present"""
    # Ensure no key is set
    os.environ.pop('TOKLIGENCE_OPENAI_API_KEY', None)
    os.environ.pop('OPENAI_API_KEY', None)

    detector = LLMDetector()
    await detector._detect_openai()

    assert len(detector.endpoints) == 0


@pytest.mark.asyncio
async def test_detect_anthropic_with_key():
    """Test Anthropic detection when API key is present"""
    os.environ['TOKLIGENCE_ANTHROPIC_API_KEY'] = 'sk-ant-test123'

    detector = LLMDetector()
    await detector._detect_anthropic()

    assert len(detector.endpoints) == 1
    endpoint = detector.endpoints[0]
    assert endpoint.type == 'anthropic'
    assert endpoint.name == 'Anthropic API'
    assert endpoint.available

    # Cleanup
    del os.environ['TOKLIGENCE_ANTHROPIC_API_KEY']


@pytest.mark.asyncio
async def test_detect_google_with_key():
    """Test Google Gemini detection when API key is present"""
    os.environ['TOKLIGENCE_GOOGLE_API_KEY'] = 'test-google-key'

    detector = LLMDetector()
    await detector._detect_google()

    assert len(detector.endpoints) == 1
    endpoint = detector.endpoints[0]
    assert endpoint.type == 'google'
    assert endpoint.name == 'Google Gemini API'
    assert endpoint.available

    # Cleanup
    del os.environ['TOKLIGENCE_GOOGLE_API_KEY']


@pytest.mark.asyncio
async def test_get_available_endpoints():
    """Test getting available endpoints"""
    os.environ['TOKLIGENCE_OPENAI_API_KEY'] = 'sk-test'

    detector = LLMDetector()
    await detector.detect_all()

    available = detector.get_available_endpoints()
    assert isinstance(available, list)
    assert len(available) > 0

    # Cleanup
    del os.environ['TOKLIGENCE_OPENAI_API_KEY']


@pytest.mark.asyncio
async def test_get_best_endpoint():
    """Test getting best endpoint (highest priority)"""
    os.environ['TOKLIGENCE_OPENAI_API_KEY'] = 'sk-test'
    os.environ['TOKLIGENCE_ANTHROPIC_API_KEY'] = 'sk-ant-test'

    detector = LLMDetector()
    await detector.detect_all()

    best = detector.get_best_endpoint()
    assert best is not None
    # OpenAI has higher priority (100 vs 95)
    assert best.type == 'openai'

    # Cleanup
    del os.environ['TOKLIGENCE_OPENAI_API_KEY']
    del os.environ['TOKLIGENCE_ANTHROPIC_API_KEY']


@pytest.mark.asyncio
async def test_select_endpoint_with_preference():
    """Test endpoint selection with preference"""
    os.environ['TOKLIGENCE_OPENAI_API_KEY'] = 'sk-test'
    os.environ['TOKLIGENCE_ANTHROPIC_API_KEY'] = 'sk-ant-test'

    detector = LLMDetector()
    await detector.detect_all()

    # Prefer Anthropic even though OpenAI has higher priority
    endpoint = await select_endpoint(detector, preference='anthropic')
    assert endpoint.type == 'anthropic'

    # Cleanup
    del os.environ['TOKLIGENCE_OPENAI_API_KEY']
    del os.environ['TOKLIGENCE_ANTHROPIC_API_KEY']


@pytest.mark.asyncio
async def test_select_endpoint_no_endpoints():
    """Test endpoint selection when no endpoints are available"""
    # Create a detector with no endpoints (don't call detect_all)
    detector = LLMDetector()
    # detector.endpoints is empty by default

    with pytest.raises(RuntimeError, match="No LLM endpoints available"):
        await select_endpoint(detector)
