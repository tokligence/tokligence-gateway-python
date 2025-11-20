"""
LLM Client Factory

Creates appropriate clients for different LLM providers
"""

from typing import Any, Optional, Dict, List, AsyncIterator
from .detector import Endpoint


def create_client(endpoint: Endpoint) -> Any:
    """
    Create appropriate client for endpoint type

    Args:
        endpoint: Endpoint configuration

    Returns:
        Client instance (OpenAI, Anthropic, or Google client)

    Raises:
        ImportError: If required SDK is not installed
    """
    if endpoint.type == 'openai':
        try:
            from openai import AsyncOpenAI
            import os

            # For remote OpenAI, use API key
            api_key = os.getenv('TOKLIGENCE_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
            # For local endpoints (vLLM, LM Studio), API key is not required
            if not api_key and not endpoint.local:
                raise ValueError("OpenAI API key not found")

            return AsyncOpenAI(
                api_key=api_key or 'not-needed',  # Local endpoints don't need real keys
                base_url=endpoint.base_url
            )
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

    elif endpoint.type == 'anthropic':
        try:
            from anthropic import AsyncAnthropic
            import os

            api_key = os.getenv('TOKLIGENCE_ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("Anthropic API key not found")

            return AsyncAnthropic(
                api_key=api_key,
                base_url=endpoint.base_url if endpoint.base_url != 'https://api.anthropic.com' else None
            )
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

    elif endpoint.type == 'google':
        try:
            import google.generativeai as genai
            import os

            api_key = os.getenv('TOKLIGENCE_GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Google API key not found")

            genai.configure(api_key=api_key)
            return genai
        except ImportError:
            raise ImportError(
                "Google Generative AI SDK not installed. Install with: pip install google-generativeai"
            )

    elif endpoint.type == 'ollama':
        try:
            from openai import AsyncOpenAI

            # Ollama uses OpenAI-compatible API without auth
            return AsyncOpenAI(
                api_key='ollama',  # Ollama doesn't need real API key
                base_url=f'{endpoint.base_url}/v1'
            )
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

    else:
        raise ValueError(f"Unsupported endpoint type: {endpoint.type}")


def get_model(endpoint: Endpoint, user_preference: Optional[str] = None) -> str:
    """
    Get model name to use

    Args:
        endpoint: Endpoint configuration
        user_preference: Optional user-specified model

    Returns:
        Model name to use
    """
    if user_preference:
        return user_preference

    return endpoint.default_model or 'gpt-4o-mini'


async def create_streaming_chat(
    client: Any,
    endpoint: Endpoint,
    model: str,
    messages: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> AsyncIterator:
    """
    Create streaming chat completion

    Args:
        client: LLM client instance
        endpoint: Endpoint configuration
        model: Model name
        messages: Chat messages
        options: Optional parameters (tools, temperature, max_tokens, etc.)

    Returns:
        Async iterator for streaming response

    Yields:
        Streaming chunks from the LLM
    """
    options = options or {}

    if endpoint.type == 'openai' or endpoint.type == 'ollama':
        # OpenAI-compatible API
        create_params = {
            'model': model,
            'messages': messages,
            'stream': True,
        }

        if 'temperature' in options:
            create_params['temperature'] = options['temperature']
        if 'maxTokens' in options or 'max_tokens' in options:
            create_params['max_tokens'] = options.get('maxTokens') or options.get('max_tokens')
        if 'tools' in options and options['tools']:
            create_params['tools'] = options['tools']

        stream = await client.chat.completions.create(**create_params)
        return stream

    elif endpoint.type == 'anthropic':
        # Anthropic API
        # Need to convert OpenAI-style messages to Anthropic format
        system_messages = [m['content'] for m in messages if m['role'] == 'system']
        other_messages = [m for m in messages if m['role'] != 'system']

        create_params = {
            'model': model,
            'messages': other_messages,
            'max_tokens': options.get('maxTokens') or options.get('max_tokens', 2048),
            'stream': True,
        }

        if system_messages:
            create_params['system'] = '\n\n'.join(system_messages)
        if 'temperature' in options:
            create_params['temperature'] = options['temperature']
        if 'tools' in options and options['tools']:
            # Convert OpenAI tools to Anthropic tools
            create_params['tools'] = [
                {
                    'name': tool['function']['name'],
                    'description': tool['function']['description'],
                    'input_schema': tool['function']['parameters']
                }
                for tool in options['tools']
            ]

        stream = await client.messages.create(**create_params)
        return stream

    elif endpoint.type == 'google':
        # Google Gemini API
        # Extract system message
        system_messages = [m['content'] for m in messages if m['role'] == 'system']
        other_messages = [m for m in messages if m['role'] != 'system']

        # Convert to Gemini format
        gemini_messages = []
        for msg in other_messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_messages.append({
                'role': role,
                'parts': [msg['content']]
            })

        # Create model
        model_instance = client.GenerativeModel(
            model_name=model,
            system_instruction=system_messages[0] if system_messages else None
        )

        # Start chat
        chat = model_instance.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

        # Send message and stream
        response = await chat.send_message_async(
            gemini_messages[-1]['parts'][0] if gemini_messages else '',
            stream=True
        )

        return response

    else:
        raise ValueError(f"Unsupported endpoint type: {endpoint.type}")
