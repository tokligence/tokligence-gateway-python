"""
Tokligence - Multi-platform LLM gateway with unified OpenAI-compatible API

Python wrapper for the Tokligence Gateway.
"""

__version__ = "0.4.0"
__author__ = "Tokligence Team"
__email__ = "cs@tokligence.ai"

from .gateway import Gateway
from .daemon import Daemon
from .config import Config, load_config

__all__ = ["Gateway", "Daemon", "Config", "load_config"]