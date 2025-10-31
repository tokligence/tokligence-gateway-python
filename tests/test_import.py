"""
Basic import tests for tokligence
"""

import pytest


def test_import():
    """Test that the package can be imported."""
    import tokligence
    assert tokligence.__version__ == "0.2.0"


def test_import_components():
    """Test that main components can be imported."""
    from tokligence import Gateway, Daemon, Config, load_config

    # Check that classes are importable
    assert Gateway is not None
    assert Daemon is not None
    assert Config is not None
    assert load_config is not None


def test_config_defaults():
    """Test that default configuration is generated correctly."""
    from tokligence.config import Config

    config = Config()
    defaults = config.get_defaults()

    assert 'gateway' in defaults
    assert 'providers' in defaults
    assert 'database' in defaults
    assert defaults['gateway']['port'] == 8081