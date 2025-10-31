"""
Configuration management for tokligence
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .utils import get_default_config_path


class Config:
    """Configuration manager for Tokligence Gateway."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = Path(config_path) if config_path else get_default_config_path()
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            return self.get_defaults()

        with open(self.config_path, 'r') as f:
            if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
                return yaml.safe_load(f) or {}
            elif self.config_path.suffix == '.json':
                return json.load(f)
            else:
                # Try to auto-detect format
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content) or {}

    def save(self, data: Optional[Dict[str, Any]] = None):
        """
        Save configuration to file.

        Args:
            data: Configuration data to save (uses self.data if not provided)
        """
        if data is None:
            data = self.data

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
                yaml.safe_dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        data = self.data

        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def update(self, updates: Dict[str, Any]):
        """
        Update configuration with multiple values.

        Args:
            updates: Dictionary of updates
        """
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        self.data = deep_update(self.data, updates)

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            'gateway': {
                'host': 'localhost',
                'port': 8081,
                'auth': {
                    'enabled': False,
                    'type': 'api_key'
                },
                'logging': {
                    'level': 'info',
                    'file': None,
                    'max_size': '100MB',
                    'max_days': 30
                }
            },
            'database': {
                'type': 'sqlite',
                'path': '~/.config/tokligence/gateway.db'
            },
            'providers': {
                'openai': {
                    'enabled': True,
                    'api_key': os.environ.get('OPENAI_API_KEY', ''),
                    'base_url': 'https://api.openai.com/v1',
                    'models': ['gpt-4', 'gpt-3.5-turbo']
                },
                'anthropic': {
                    'enabled': True,
                    'api_key': os.environ.get('ANTHROPIC_API_KEY', ''),
                    'base_url': 'https://api.anthropic.com',
                    'models': ['claude-3-opus', 'claude-3-sonnet']
                },
                'loopback': {
                    'enabled': True,
                    'models': ['loopback']
                }
            },
            'marketplace': {
                'enabled': False,
                'api_url': 'https://api.tokligence.ai',
                'update_check': True
            }
        }

    def to_env_vars(self) -> Dict[str, str]:
        """
        Convert configuration to environment variables.

        Returns:
            Dictionary of environment variables
        """
        env_vars = {}

        def flatten(d, prefix='TOKLIGENCE'):
            for key, value in d.items():
                env_key = f"{prefix}_{key.upper()}"
                if isinstance(value, dict):
                    flatten(value, env_key)
                elif isinstance(value, bool):
                    env_vars[env_key] = 'true' if value else 'false'
                elif value is not None:
                    env_vars[env_key] = str(value)

        flatten(self.data)
        return env_vars


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Config instance
    """
    return Config(config_path)


def save_config(config: Config, config_path: Optional[str] = None):
    """
    Save configuration to file.

    Args:
        config: Config instance to save
        config_path: Optional path to save to
    """
    if config_path:
        config.config_path = Path(config_path)
    config.save()