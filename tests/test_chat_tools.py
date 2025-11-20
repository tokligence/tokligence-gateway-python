"""
Tests for chat tools module
"""

import pytest
from tokligence.chat.tools import (
    is_sensitive_config_key,
    mask_sensitive_value,
    get_platform_info,
    TOOLS,
    execute_tool,
    parse_tool_calls
)


def test_is_sensitive_config_key():
    """Test sensitive key detection"""
    # Sensitive keys
    assert is_sensitive_config_key('api_key')
    assert is_sensitive_config_key('openai_api_key')
    assert is_sensitive_config_key('secret')
    assert is_sensitive_config_key('password')
    assert is_sensitive_config_key('token')
    assert is_sensitive_config_key('email')

    # Non-sensitive keys
    assert not is_sensitive_config_key('work_mode')
    assert not is_sensitive_config_key('log_level')
    assert not is_sensitive_config_key('port')


def test_mask_sensitive_value():
    """Test value masking"""
    # Test masking
    masked = mask_sensitive_value('sk-1234567890abcdef')
    assert '***redacted***' in masked
    assert 'len=' in masked
    assert 'prefix=' in masked
    assert 'sk-1234567890abcdef' not in masked

    # Test empty value
    masked_empty = mask_sensitive_value('')
    assert masked_empty == ''

    # Test None
    masked_none = mask_sensitive_value(None)
    assert masked_none == ''


def test_get_platform_info():
    """Test platform info retrieval"""
    info = get_platform_info()

    assert 'platform' in info
    assert 'isWindows' in info
    assert 'isMac' in info
    assert 'isLinux' in info
    assert 'pathSeparator' in info
    assert 'homeDir' in info

    # Exactly one should be True
    platform_flags = [info['isWindows'], info['isMac'], info['isLinux']]
    assert sum(platform_flags) == 1


def test_tools_definition():
    """Test that tools are properly defined"""
    assert isinstance(TOOLS, list)
    assert len(TOOLS) > 0

    # Check tool structure
    for tool in TOOLS:
        assert 'type' in tool
        assert tool['type'] == 'function'
        assert 'function' in tool
        assert 'name' in tool['function']
        assert 'description' in tool['function']
        assert 'parameters' in tool['function']

    # Check for expected tools
    tool_names = [t['function']['name'] for t in TOOLS]
    expected_tools = ['set_config', 'get_config', 'get_status', 'start_gateway', 'stop_gateway', 'search_docs', 'get_doc']
    for expected in expected_tools:
        assert expected in tool_names, f"Expected tool '{expected}' not found"


@pytest.mark.asyncio
async def test_execute_tool_search_docs():
    """Test search_docs tool execution"""
    result = await execute_tool('search_docs', {'query': 'OpenAI'})

    assert isinstance(result, dict)
    assert result['success']
    assert 'query' in result
    assert 'results' in result
    assert 'count' in result
    assert isinstance(result['results'], list)


@pytest.mark.asyncio
async def test_execute_tool_get_doc():
    """Test get_doc tool execution"""
    result = await execute_tool('get_doc', {'name': 'README'})

    assert isinstance(result, dict)
    assert result['success']
    assert 'name' in result
    assert 'content' in result
    assert isinstance(result['content'], str)
    assert len(result['content']) > 0


@pytest.mark.asyncio
async def test_execute_tool_get_doc_not_found():
    """Test get_doc with non-existent document"""
    result = await execute_tool('get_doc', {'name': 'NONEXISTENT'})

    assert isinstance(result, dict)
    assert not result['success']
    assert 'message' in result
    assert 'available' in result


@pytest.mark.asyncio
async def test_execute_tool_unknown():
    """Test execution of unknown tool"""
    result = await execute_tool('unknown_tool', {})

    assert isinstance(result, dict)
    assert not result['success']
    assert 'Unknown tool' in result['message']


def test_parse_tool_calls():
    """Test parsing tool calls from message"""
    import json

    message = {
        'role': 'assistant',
        'content': None,
        'tool_calls': [
            {
                'id': 'call_123',
                'type': 'function',
                'function': {
                    'name': 'search_docs',
                    'arguments': json.dumps({'query': 'test'})
                }
            }
        ]
    }

    parsed = parse_tool_calls(message)

    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]['id'] == 'call_123'
    assert parsed[0]['name'] == 'search_docs'
    assert parsed[0]['args'] == {'query': 'test'}


def test_parse_tool_calls_empty():
    """Test parsing message with no tool calls"""
    message = {
        'role': 'assistant',
        'content': 'Hello'
    }

    parsed = parse_tool_calls(message)
    assert parsed == []
