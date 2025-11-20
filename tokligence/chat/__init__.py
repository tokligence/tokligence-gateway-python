"""
Chat module for Tokligence Gateway

Interactive AI assistant for configuration and troubleshooting.
"""

import asyncio
from .session import start_chat as async_start_chat


def start_chat(model=None):
    """
    Synchronous wrapper for start_chat

    Args:
        model: Optional preferred model name
    """
    asyncio.run(async_start_chat(model=model))


__all__ = ['start_chat']
