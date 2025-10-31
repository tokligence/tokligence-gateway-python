"""
Gateway wrapper for the Tokligence Gateway CLI
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from .utils import find_available_binary


class Gateway:
    """
    Python wrapper for the Tokligence Gateway CLI tool.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Gateway wrapper.

        Args:
            config_path: Optional path to configuration file
        """
        self.binary_path = find_available_binary('gateway')
        if not self.binary_path:
            raise RuntimeError(
                "Gateway binary not found. Please ensure it's installed correctly."
            )
        self.config_path = config_path

    def run(self, args: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """
        Run a gateway command.

        Args:
            args: Command arguments
            capture_output: Whether to capture output

        Returns:
            CompletedProcess instance
        """
        cmd = [str(self.binary_path)]

        # Add config file if specified
        if self.config_path:
            cmd.extend(['--config', self.config_path])

        cmd.extend(args)

        if capture_output:
            return subprocess.run(cmd, capture_output=True, text=True, check=False)
        else:
            return subprocess.run(cmd, check=False)

    def init(self, force: bool = False) -> bool:
        """
        Initialize gateway configuration.

        Args:
            force: Force overwrite existing configuration

        Returns:
            True if successful
        """
        args = ['init']
        if force:
            args.append('--force')

        result = self.run(args)
        return result.returncode == 0

    def create_user(self, username: str, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            username: Username
            email: Optional email address

        Returns:
            User information dict
        """
        args = ['user', 'create', username]
        if email:
            args.extend(['--email', email])

        result = self.run(args, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create user: {result.stderr}")

        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"message": result.stdout.strip()}

    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users.

        Returns:
            List of user dictionaries
        """
        result = self.run(['user', 'list', '--json'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list users: {result.stderr}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    def create_api_key(self, user_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an API key for a user.

        Args:
            user_id: User ID
            name: Optional key name

        Returns:
            API key information
        """
        args = ['apikey', 'create', user_id]
        if name:
            args.extend(['--name', name])

        result = self.run(args, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create API key: {result.stderr}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"message": result.stdout.strip()}

    def list_providers(self) -> List[Dict[str, Any]]:
        """
        List available providers.

        Returns:
            List of provider dictionaries
        """
        result = self.run(['provider', 'list', '--json'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list providers: {result.stderr}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    def get_usage(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics.

        Args:
            user_id: Optional user ID for filtering

        Returns:
            Usage statistics dictionary
        """
        args = ['usage']
        if user_id:
            args.extend(['--user', user_id])
        args.append('--json')

        result = self.run(args, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get usage: {result.stderr}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}