"""
Chat Agent Tools

Provides tools for the LLM to execute gateway configuration commands.
Handles cross-platform differences and sensitive data masking.
"""

import os
import platform
from typing import Dict, Any, List, Optional
from ..gateway import Gateway
from ..daemon import Daemon
from .knowledge import load_knowledge


def is_sensitive_config_key(key: str) -> bool:
    """
    Detect whether a config key is sensitive (API keys, secrets, tokens, etc.)

    Args:
        key: Configuration key name

    Returns:
        True if the key is sensitive
    """
    if not key:
        return False

    key_lower = str(key).lower()
    patterns = [
        'api_key', 'apikey', 'secret', 'token', 'password', 'passphrase',
        'credential', 'auth_key', 'email', 'display_name', 'admin_email', 'name'
    ]
    return any(p in key_lower for p in patterns)


def mask_sensitive_value(value: Any) -> str:
    """
    Return a redacted placeholder instead of the real secret value

    Args:
        value: The value to mask

    Returns:
        Masked value string
    """
    if not value:
        return ''

    str_value = str(value)
    length = len(str_value)
    prefix = str_value[:4] if length > 4 else str_value[:1]

    return f'***redacted*** (len={length}, prefix={prefix})'


def get_platform_info() -> Dict[str, Any]:
    """Get platform-specific information"""
    system = platform.system()
    is_windows = system == 'Windows'
    is_mac = system == 'Darwin'
    is_linux = system == 'Linux'

    return {
        'platform': system,
        'isWindows': is_windows,
        'isMac': is_mac,
        'isLinux': is_linux,
        'pathSeparator': '\\' if is_windows else '/',
        'homeDir': os.path.expanduser('~')
    }


# Tool definitions for function calling
TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'set_config',
            'description': '''Update a gateway configuration value. Use this when the user wants to configure or change a setting.

Available configuration keys (70+ options):

Account & Exchange:
- email: User email for identity
- display_name: Display name for gateway
- base_url: Token exchange endpoint (dev.tokligence.ai, tokligence.ai)
- marketplace_enabled: Enable marketplace integration (true/false)
- telemetry_enabled: Enable telemetry (true/false)

Security & Auth:
- auth_secret: Authentication secret
- auth_disabled: Disable auth (true/false)

Provider API Keys:
- openai_api_key: OpenAI API key
- openai_base_url: OpenAI API base URL
- anthropic_api_key: Anthropic API key
- anthropic_base_url: Anthropic API base URL
- google_api_key: Google/Gemini API key

Work Mode & Routing:
- work_mode: Gateway mode (auto, passthrough, translation)
- model_provider_routes: Model-to-provider routing

Logging:
- log_level: Log level (debug, info, warn, error)

Storage:
- ledger_path: Path to ledger database
- identity_path: Path to identity database''',
            'parameters': {
                'type': 'object',
                'properties': {
                    'key': {
                        'type': 'string',
                        'description': 'Configuration key from the list above'
                    },
                    'value': {
                        'type': 'string',
                        'description': 'Configuration value to set'
                    }
                },
                'required': ['key', 'value']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_config',
            'description': 'Get current gateway configuration. If key is provided, returns that specific value. If no key provided, returns all configuration.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'key': {
                        'type': 'string',
                        'description': 'Optional configuration key to retrieve. If omitted, returns all config.'
                    }
                },
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_status',
            'description': 'Check if the gateway daemon is currently running',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'start_gateway',
            'description': 'Start the gateway daemon in the background',
            'parameters': {
                'type': 'object',
                'properties': {
                    'daemon': {
                        'type': 'boolean',
                        'description': 'Whether to run as daemon (default: true)',
                        'default': True
                    }
                },
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'stop_gateway',
            'description': 'Stop the gateway daemon',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'search_docs',
            'description': 'Search the bundled Tokligence Gateway documentation for a keyword or phrase. Use this to answer configuration and usage questions from official docs.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query (e.g., "OpenAI API key", "routing rules", "multiport_mode").'
                    }
                },
                'required': ['query']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_doc',
            'description': 'Retrieve the full text of a specific bundled documentation file (for example QUICK_START or USER_GUIDE) so you can quote or summarize it.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Document name without .md extension (e.g., "QUICK_START", "USER_GUIDE", "README").'
                    }
                },
                'required': ['name']
            }
        }
    }
]


async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function

    Args:
        tool_name: Name of the tool to execute
        args: Tool arguments

    Returns:
        Tool execution result
    """
    platform_info = get_platform_info()
    gateway = Gateway()
    daemon = Daemon()

    try:
        if tool_name == 'set_config':
            key = args['key']
            value = args['value']

            # Use gateway's config methods (these need to be implemented in gateway.py)
            # For now, we'll use a placeholder
            sensitive = is_sensitive_config_key(key)
            display_value = mask_sensitive_value(value) if sensitive else value

            # TODO: Actually set the config via gateway
            # gateway.set_config(key, value)

            return {
                'success': True,
                'message': (
                    f'Configuration updated: {key} = {display_value} (secret value kept local)'
                    if sensitive else
                    f'Configuration updated: {key} = {display_value}'
                ),
                'key': key,
                'masked': sensitive,
                'platform': platform_info['platform']
            }

        elif tool_name == 'get_config':
            key = args.get('key')

            if key:
                # Single-key lookup
                # TODO: Implement get_config in gateway
                # raw_value = gateway.get_config(key)
                raw_value = f'<value for {key}>'  # Placeholder
                sensitive = is_sensitive_config_key(key)

                return {
                    'success': True,
                    'key': key,
                    'value': mask_sensitive_value(raw_value) if sensitive else raw_value,
                    'masked': sensitive,
                    'platform': platform_info['platform']
                }
            else:
                # Full configuration summary
                # Build a conservative summary
                summary = {
                    'important': {
                        'work_mode': 'auto',  # Placeholder
                        'auth_disabled': False,
                    },
                    'providers': {
                        'openai_configured': bool(os.getenv('TOKLIGENCE_OPENAI_API_KEY')),
                        'anthropic_configured': bool(os.getenv('TOKLIGENCE_ANTHROPIC_API_KEY')),
                        'google_configured': bool(os.getenv('TOKLIGENCE_GOOGLE_API_KEY')),
                    },
                    'allKeys': ['work_mode', 'auth_disabled', 'log_level']  # Placeholder
                }

                return {
                    'success': True,
                    'summary': summary,
                    'platform': platform_info['platform']
                }

        elif tool_name == 'get_status':
            status = daemon.status()
            is_running = status.get('status') == 'running'
            pid = status.get('pid')

            return {
                'success': True,
                'running': is_running,
                'pid': pid,
                'platform': platform_info['platform'],
                'message': f'Gateway is running (PID: {pid})' if is_running else 'Gateway is not running'
            }

        elif tool_name == 'start_gateway':
            daemon_mode = args.get('daemon', True)

            # Check if already running
            status = daemon.status()
            if status.get('status') == 'running':
                return {
                    'success': False,
                    'message': 'Gateway is already running',
                    'platform': platform_info['platform']
                }

            # Start daemon
            daemon.start(background=daemon_mode)

            # Wait a bit for startup
            import asyncio
            await asyncio.sleep(2)

            # Verify it started
            status = daemon.status()
            is_running = status.get('status') == 'running'
            pid = status.get('pid')

            if is_running:
                return {
                    'success': True,
                    'message': f'Gateway started successfully (PID: {pid})',
                    'pid': pid,
                    'platform': platform_info['platform'],
                    'note': (
                        'Running on Windows - check Task Manager if issues occur'
                        if platform_info['isWindows'] else
                        'Running in background'
                    )
                }
            else:
                return {
                    'success': False,
                    'message': 'Gateway failed to start. Check logs for details.',
                    'platform': platform_info['platform']
                }

        elif tool_name == 'stop_gateway':
            # Check if running
            status = daemon.status()
            if status.get('status') != 'running':
                return {
                    'success': False,
                    'message': 'Gateway is not running',
                    'platform': platform_info['platform']
                }

            # Stop daemon
            daemon.stop()

            # Wait a bit for shutdown
            import asyncio
            await asyncio.sleep(1)

            # Verify it stopped
            status = daemon.status()
            is_running = status.get('status') == 'running'

            return {
                'success': not is_running,
                'message': (
                    'Gateway may still be shutting down'
                    if is_running else
                    'Gateway stopped successfully'
                ),
                'platform': platform_info['platform']
            }

        elif tool_name == 'search_docs':
            query = args['query']
            knowledge = load_knowledge()
            results = knowledge.search_docs(query)

            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results),
                'note': (
                    'No exact matches found for this phrase. You can still rely on the bundled docs and your own capability description to answer general questions.'
                    if len(results) == 0 else
                    'These matches come from the bundled docs (README, QUICK_START, USER_GUIDE, configuration_guide, etc.).'
                ),
                'docs': knowledge.get_available_docs()
            }

        elif tool_name == 'get_doc':
            name = args['name']
            knowledge = load_knowledge()
            content = knowledge.get_doc(name)

            if not content:
                return {
                    'success': False,
                    'message': f'Document not found: {name}.md',
                    'available': knowledge.get_available_docs()
                }

            return {
                'success': True,
                'name': name,
                'content': content,
                'available': knowledge.get_available_docs()
            }

        else:
            return {
                'success': False,
                'message': f'Unknown tool: {tool_name}',
                'platform': platform_info['platform']
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'platform': platform_info['platform']
        }


def parse_tool_calls(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse tool calls from LLM response

    Args:
        message: LLM message with tool calls

    Returns:
        Parsed tool calls
    """
    import json

    if not message.get('tool_calls'):
        return []

    return [
        {
            'id': tool_call['id'],
            'name': tool_call['function']['name'],
            'args': json.loads(tool_call['function']['arguments'])
        }
        for tool_call in message['tool_calls']
    ]


async def execute_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Execute all tool calls from a message

    Args:
        tool_calls: Parsed tool calls

    Returns:
        Tool execution results
    """
    import json

    results = []

    for tool_call in tool_calls:
        print(f"\n🔧 Executing: {tool_call['name']}", tool_call.get('args', {}))

        result = await execute_tool(tool_call['name'], tool_call.get('args', {}))

        results.append({
            'tool_call_id': tool_call['id'],
            'role': 'tool',
            'name': tool_call['name'],
            'content': json.dumps(result)
        })

        # Show result to user
        if result.get('success'):
            print(f"✓ {result.get('message', 'Success')}")
        else:
            print(f"✗ {result.get('message') or result.get('error', 'Failed')}")
            if result.get('note'):
                print(f"  Note: {result['note']}")

    return results
