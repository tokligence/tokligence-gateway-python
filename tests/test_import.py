"""
Basic import tests for tokligence
"""

import pytest


def test_import():
    """Test that the package can be imported."""
    import tokligence
    # Version should be a valid semver string
    assert tokligence.__version__ is not None
    parts = tokligence.__version__.split('.')
    assert len(parts) >= 2, "Version should be semver format (x.y.z)"


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