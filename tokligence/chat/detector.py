"""
LLM Endpoint Detector

Detects available LLM endpoints (OpenAI, Anthropic, Gemini, Ollama, etc.)
"""

import os
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class Endpoint:
    """Represents an LLM endpoint"""
    name: str
    type: str  # 'openai', 'anthropic', 'google', 'ollama', etc.
    base_url: str
    available: bool
    local: bool = False
    default_model: Optional[str] = None
    priority: int = 0  # Higher priority = preferred


class LLMDetector:
    """Detects and manages available LLM endpoints"""

    def __init__(self):
        self.endpoints: List[Endpoint] = []

    async def detect_all(self):
        """Detect all available LLM endpoints"""
        detection_tasks = [
            self._detect_openai(),
            self._detect_anthropic(),
            self._detect_google(),
            self._detect_ollama(),
            self._detect_vllm(),
            self._detect_lm_studio(),
        ]

        # Run all detections concurrently
        await asyncio.gather(*detection_tasks, return_exceptions=True)

        # Sort by priority (highest first)
        self.endpoints.sort(key=lambda e: e.priority, reverse=True)

    async def _detect_openai(self):
        """Detect OpenAI API endpoint"""
        api_key = os.getenv('TOKLIGENCE_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('TOKLIGENCE_OPENAI_BASE_URL') or os.getenv('OPENAI_BASE_URL') or 'https://api.openai.com/v1'

        if api_key:
            self.endpoints.append(Endpoint(
                name='OpenAI API',
                type='openai',
                base_url=base_url,
                available=True,
                local=False,
                default_model='gpt-4o-mini',
                priority=100
            ))

    async def _detect_anthropic(self):
        """Detect Anthropic API endpoint"""
        api_key = os.getenv('TOKLIGENCE_ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        base_url = os.getenv('TOKLIGENCE_ANTHROPIC_BASE_URL') or os.getenv('ANTHROPIC_BASE_URL') or 'https://api.anthropic.com'

        if api_key:
            self.endpoints.append(Endpoint(
                name='Anthropic API',
                type='anthropic',
                base_url=base_url,
                available=True,
                local=False,
                default_model='claude-sonnet-4.5-20250514',
                priority=95
            ))

    async def _detect_google(self):
        """Detect Google Gemini API endpoint"""
        api_key = os.getenv('TOKLIGENCE_GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

        if api_key:
            self.endpoints.append(Endpoint(
                name='Google Gemini API',
                type='google',
                base_url='https://generativelanguage.googleapis.com',
                available=True,
                local=False,
                default_model='gemini-2.0-flash-exp',
                priority=90
            ))

    async def _detect_ollama(self):
        """Detect local Ollama endpoint"""
        base_url = os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434'

        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f'{base_url}/api/tags')
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    default_model = models[0]['name'] if models else 'llama3.2'

                    self.endpoints.append(Endpoint(
                        name='Ollama (Local)',
                        type='ollama',
                        base_url=base_url,
                        available=True,
                        local=True,
                        default_model=default_model,
                        priority=80
                    ))
        except Exception:
            # Ollama not available
            pass

    async def _detect_vllm(self):
        """Detect local vLLM endpoint"""
        base_url = os.getenv('VLLM_BASE_URL') or 'http://localhost:8000'

        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f'{base_url}/v1/models')
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('data', [])
                    default_model = models[0]['id'] if models else 'default'

                    self.endpoints.append(Endpoint(
                        name='vLLM (Local)',
                        type='openai',  # vLLM uses OpenAI-compatible API
                        base_url=f'{base_url}/v1',
                        available=True,
                        local=True,
                        default_model=default_model,
                        priority=70
                    ))
        except Exception:
            # vLLM not available
            pass

    async def _detect_lm_studio(self):
        """Detect local LM Studio endpoint"""
        base_url = os.getenv('LM_STUDIO_BASE_URL') or 'http://localhost:1234'

        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f'{base_url}/v1/models')
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('data', [])
                    default_model = models[0]['id'] if models else 'local-model'

                    self.endpoints.append(Endpoint(
                        name='LM Studio (Local)',
                        type='openai',  # LM Studio uses OpenAI-compatible API
                        base_url=f'{base_url}/v1',
                        available=True,
                        local=True,
                        default_model=default_model,
                        priority=60
                    ))
        except Exception:
            # LM Studio not available
            pass

    def get_available_endpoints(self) -> List[Endpoint]:
        """Get list of available endpoints"""
        return [e for e in self.endpoints if e.available]

    def get_endpoint_by_type(self, endpoint_type: str) -> Optional[Endpoint]:
        """Get endpoint by type"""
        for endpoint in self.endpoints:
            if endpoint.type == endpoint_type and endpoint.available:
                return endpoint
        return None

    def get_best_endpoint(self) -> Optional[Endpoint]:
        """Get the best available endpoint (highest priority)"""
        available = self.get_available_endpoints()
        return available[0] if available else None


async def select_endpoint(detector: LLMDetector, preference: Optional[str] = None) -> Endpoint:
    """
    Select the best endpoint based on preference

    Args:
        detector: LLMDetector instance
        preference: Optional preferred endpoint type

    Returns:
        Selected Endpoint

    Raises:
        RuntimeError: If no endpoints are available
    """
    # If user has a preference, try to use it
    if preference:
        endpoint = detector.get_endpoint_by_type(preference)
        if endpoint:
            return endpoint

    # Otherwise, get the best available endpoint
    endpoint = detector.get_best_endpoint()
    if not endpoint:
        raise RuntimeError(
            "No LLM endpoints available. Please configure at least one:\n"
            "  - OpenAI: export TOKLIGENCE_OPENAI_API_KEY=sk-...\n"
            "  - Anthropic: export TOKLIGENCE_ANTHROPIC_API_KEY=sk-ant-...\n"
            "  - Google Gemini: export TOKLIGENCE_GOOGLE_API_KEY=...\n"
            "  - Or run a local LLM (Ollama, vLLM, LM Studio)"
        )

    return endpoint
