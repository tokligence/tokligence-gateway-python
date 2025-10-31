"""
Daemon wrapper for the Tokligence Gateway daemon (gatewayd)
"""

import os
import subprocess
import sys
import time
import signal
import atexit
from pathlib import Path
from typing import Optional, Dict, Any
from .utils import find_available_binary, ensure_config_dir


class Daemon:
    """
    Python wrapper for the Tokligence Gateway daemon (gatewayd).
    """

    def __init__(self, config_path: Optional[str] = None, port: int = 8081):
        """
        Initialize the Daemon wrapper.

        Args:
            config_path: Optional path to configuration file
            port: Port to run the daemon on (default: 8081)
        """
        self.binary_path = find_available_binary('gatewayd')
        if not self.binary_path:
            raise RuntimeError(
                "Gatewayd binary not found. Please ensure it's installed correctly."
            )
        self.config_path = config_path
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, self._signal_handler)
        atexit.register(self.stop)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.stop()
        sys.exit(0)

    def start(self, background: bool = False, **kwargs) -> Optional[subprocess.Popen]:
        """
        Start the gateway daemon.

        Args:
            background: Run in background (detached)
            **kwargs: Additional environment variables

        Returns:
            Process instance if running in foreground, None if in background
        """
        if self.process and self.process.poll() is None:
            print("Daemon is already running")
            return self.process

        cmd = [str(self.binary_path)]

        # Add config file if specified
        if self.config_path:
            cmd.extend(['--config', self.config_path])

        # Add port
        cmd.extend(['--port', str(self.port)])

        # Setup environment
        env = dict(os.environ)
        env.update(kwargs)

        if background:
            # Run in background
            log_dir = ensure_config_dir() / 'logs'
            log_dir.mkdir(exist_ok=True)

            stdout_log = open(log_dir / 'gatewayd.log', 'a')
            stderr_log = open(log_dir / 'gatewayd.error.log', 'a')

            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=stdout_log,
                stderr=stderr_log,
                start_new_session=True
            )

            # Save PID for later reference
            pid_file = ensure_config_dir() / 'gatewayd.pid'
            pid_file.write_text(str(self.process.pid))

            print(f"Daemon started in background (PID: {self.process.pid})")
            return None
        else:
            # Run in foreground
            self.process = subprocess.Popen(cmd, env=env)
            return self.process

    def stop(self):
        """Stop the gateway daemon."""
        if self.process and self.process.poll() is None:
            print("Stopping daemon...")
            self.process.terminate()

            # Wait up to 10 seconds for graceful shutdown
            for _ in range(10):
                if self.process.poll() is not None:
                    break
                time.sleep(1)

            # Force kill if still running
            if self.process.poll() is None:
                print("Force killing daemon...")
                self.process.kill()

            self.process = None
            print("Daemon stopped")

        # Clean up PID file
        pid_file = ensure_config_dir() / 'gatewayd.pid'
        if pid_file.exists():
            pid_file.unlink()

    def restart(self, **kwargs):
        """Restart the gateway daemon."""
        self.stop()
        time.sleep(2)  # Wait a bit before restarting
        return self.start(**kwargs)

    def status(self) -> Dict[str, Any]:
        """
        Get daemon status.

        Returns:
            Status dictionary
        """
        if self.process and self.process.poll() is None:
            return {
                "status": "running",
                "pid": self.process.pid,
                "port": self.port
            }
        else:
            # Check for PID file
            pid_file = ensure_config_dir() / 'gatewayd.pid'
            if pid_file.exists():
                pid = int(pid_file.read_text())
                # Check if process is actually running
                try:
                    import psutil
                    if psutil.pid_exists(pid):
                        return {
                            "status": "running",
                            "pid": pid,
                            "port": self.port,
                            "note": "Running in background"
                        }
                except ImportError:
                    pass

            return {"status": "stopped"}

    def wait(self):
        """Wait for the daemon to exit."""
        if self.process:
            self.process.wait()


def main():
    """Main entry point for the daemon CLI."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Tokligence Gateway Daemon')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--port', type=int, default=8081, help='Port to listen on')
    parser.add_argument('--background', action='store_true', help='Run in background')
    parser.add_argument('command', nargs='?', default='start',
                        choices=['start', 'stop', 'restart', 'status'],
                        help='Daemon command')

    args = parser.parse_args()

    daemon = Daemon(config_path=args.config, port=args.port)

    if args.command == 'start':
        if args.background:
            daemon.start(background=True)
        else:
            process = daemon.start()
            if process:
                try:
                    process.wait()
                except KeyboardInterrupt:
                    daemon.stop()
    elif args.command == 'stop':
        daemon.stop()
    elif args.command == 'restart':
        daemon.restart(background=args.background)
    elif args.command == 'status':
        status = daemon.status()
        print(f"Status: {status['status']}")
        if status.get('pid'):
            print(f"PID: {status['pid']}")
        if status.get('port'):
            print(f"Port: {status['port']}")


if __name__ == '__main__':
    main()