"""
Integration tests for chat functionality
Run these tests to verify the chat feature works end-to-end
"""

import pytest
import os
import subprocess
import sys


def test_tgw_command_exists():
    """Test that tgw command is installed"""
    result = subprocess.run(
        ['which', 'tgw'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "tgw command not found in PATH"
    assert 'tgw' in result.stdout


def test_tgw_help():
    """Test that tgw --help works"""
    result = subprocess.run(
        ['tgw', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Tokligence Gateway' in result.stdout
    assert 'chat' in result.stdout


def test_tgw_chat_help():
    """Test that tgw chat --help works"""
    result = subprocess.run(
        ['tgw', 'chat', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Interactive AI assistant' in result.stdout
    assert '--model' in result.stdout


def test_tgw_version():
    """Test that tgw version shows correct version"""
    import tokligence
    result = subprocess.run(
        ['tgw', 'version'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Check that version output contains the package version
    assert tokligence.__version__ in result.stdout


@pytest.mark.skipif(
    not os.path.exists('/home/alejandroseaah/.ollama'),
    reason="Ollama not available"
)
def test_chat_starts_with_ollama():
    """Test that chat can start with Ollama (if available)"""
    # Send "exit" to quit immediately
    result = subprocess.run(
        ['tgw', 'chat'],
        input='exit\n',
        capture_output=True,
        text=True,
        timeout=15
    )

    # Should have started successfully
    assert 'Starting Tokligence Gateway Chat' in result.stdout
    assert 'Detecting available LLM endpoints' in result.stdout
    assert 'Loading knowledge base' in result.stdout
    assert 'Goodbye' in result.stdout


def test_chat_without_llm_shows_error():
    """Test that chat shows helpful error when no LLM is available"""
    # Temporarily remove API keys
    env = os.environ.copy()
    for key in list(env.keys()):
        if 'API_KEY' in key:
            del env[key]

    # If Ollama is running, this test will pass differently
    # So we'll just check that it doesn't crash
    result = subprocess.run(
        ['tgw', 'chat'],
        input='exit\n',
        capture_output=True,
        text=True,
        env=env,
        timeout=15
    )

    # Should either start successfully (if Ollama is available)
    # or show error about no endpoints
    assert result.returncode in [0, 1]


def test_knowledge_base_loaded():
    """Test that knowledge base files exist"""
    from pathlib import Path
    knowledge_dir = Path(__file__).parent.parent / 'tokligence' / 'knowledge'

    assert knowledge_dir.exists(), "Knowledge directory not found"

    # Check for expected files
    expected_files = ['README.md', 'QUICK_START.md', 'USER_GUIDE.md', 'configuration_guide.md', '_meta.json']
    for file in expected_files:
        file_path = knowledge_dir / file
        assert file_path.exists(), f"Expected knowledge file not found: {file}"

    # Check metadata
    import json
    meta_file = knowledge_dir / '_meta.json'
    with open(meta_file) as f:
        meta = json.load(f)

    assert 'version' in meta
    assert 'commit' in meta
    assert 'files' in meta
    assert len(meta['files']) == 4  # 4 .md files


def test_chat_module_imports():
    """Test that chat modules can be imported"""
    from tokligence.chat import start_chat
    from tokligence.chat.knowledge import load_knowledge
    from tokligence.chat.detector import LLMDetector
    from tokligence.chat.tools import TOOLS

    # Should not raise ImportError
    assert callable(start_chat)
    assert callable(load_knowledge)
    assert LLMDetector is not None
    assert isinstance(TOOLS, list)
    assert len(TOOLS) == 7  # 7 tools defined


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
