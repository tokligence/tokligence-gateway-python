"""
Utility functions for tokligence
"""

import os
import sys
import platform
import shutil
import stat
from pathlib import Path
from typing import Optional, Tuple


def get_platform_info() -> Tuple[str, str]:
    """
    Get the current platform and architecture.

    Returns:
        Tuple of (os_name, arch) e.g., ('linux', 'amd64')
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map system names
    os_map = {
        'linux': 'linux',
        'darwin': 'darwin',  # macOS
        'windows': 'windows',
    }

    # Map architecture names
    arch_map = {
        'x86_64': 'amd64',
        'amd64': 'amd64',
        'aarch64': 'arm64',
        'arm64': 'arm64',
    }

    os_name = os_map.get(system, system)
    arch = arch_map.get(machine, machine)

    return os_name, arch


def get_binary_path(binary_name: str) -> Path:
    """
    Get the path to the bundled binary.

    Args:
        binary_name: Name of the binary ('gateway' or 'gatewayd')

    Returns:
        Path to the binary executable
    """
    os_name, arch = get_platform_info()

    # Add .exe extension for Windows
    suffix = '.exe' if os_name == 'windows' else ''

    # Construct binary filename
    binary_file = f"{binary_name}-{os_name}-{arch}{suffix}"

    # Get the package directory
    package_dir = Path(__file__).parent
    binary_path = package_dir / 'binaries' / binary_file

    # Check if binary exists
    if not binary_path.exists():
        raise FileNotFoundError(
            f"Binary not found: {binary_path}\n"
            f"Platform: {os_name}/{arch}\n"
            f"This platform might not be supported."
        )

    # Ensure binary is executable (Unix-like systems)
    if os_name != 'windows':
        st = os.stat(binary_path)
        os.chmod(binary_path, st.st_mode | stat.S_IEXEC)

    return binary_path


def find_available_binary(binary_name: str) -> Optional[Path]:
    """
    Try to find an available binary, either bundled or in system PATH.

    Args:
        binary_name: Name of the binary to find

    Returns:
        Path to the binary if found, None otherwise
    """
    # First, try to get the bundled binary
    try:
        return get_binary_path(binary_name)
    except FileNotFoundError:
        pass

    # Fall back to system PATH
    system_binary = shutil.which(binary_name)
    if system_binary:
        return Path(system_binary)

    return None


def ensure_config_dir() -> Path:
    """
    Ensure the configuration directory exists.

    Returns:
        Path to the config directory
    """
    # Use XDG_CONFIG_HOME or fallback to ~/.config
    config_home = os.environ.get('XDG_CONFIG_HOME')
    if config_home:
        config_dir = Path(config_home) / 'tokligence'
    else:
        config_dir = Path.home() / '.config' / 'tokligence'

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.

    Returns:
        Path to the default config file
    """
    return ensure_config_dir() / 'config.yaml'