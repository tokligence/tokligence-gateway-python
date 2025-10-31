#!/usr/bin/env python3
"""
Basic usage example for tokligence
"""

from tokligence import Gateway, Daemon, Config
import time
import sys


def main():
    print("Tokligence Basic Usage Example")
    print("=" * 40)

    # 1. Initialize configuration
    print("\n1. Initializing configuration...")
    config = Config()

    # Set some basic configuration
    config.update({
        'gateway': {
            'port': 8081,
            'auth': {'enabled': False}  # Disable auth for testing
        },
        'providers': {
            'loopback': {'enabled': True}  # Use loopback for testing
        }
    })
    config.save()
    print("   ✓ Configuration saved")

    # 2. Initialize gateway
    print("\n2. Initializing gateway...")
    gateway = Gateway()

    try:
        if gateway.init():
            print("   ✓ Gateway initialized")
        else:
            print("   ✗ Failed to initialize gateway")
            return 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 1

    # 3. Create a test user
    print("\n3. Creating test user...")
    try:
        user = gateway.create_user("test_user", email="test@example.com")
        print(f"   ✓ User created: {user.get('username', 'test_user')}")

        # Get user ID (implementation may vary)
        user_id = user.get('id', 'test_user_id')

    except Exception as e:
        print(f"   ✗ Error creating user: {e}")
        user_id = None

    # 4. List users
    print("\n4. Listing users...")
    try:
        users = gateway.list_users()
        if users:
            for user in users:
                print(f"   - {user.get('username', 'unknown')} ({user.get('email', 'no email')})")
        else:
            print("   No users found")
    except Exception as e:
        print(f"   ✗ Error listing users: {e}")

    # 5. Start daemon
    print("\n5. Starting gateway daemon...")
    daemon = Daemon(port=8081)

    try:
        # Start in background
        daemon.start(background=True)
        print("   ✓ Daemon started")

        # Wait a moment for startup
        time.sleep(2)

        # Check status
        status = daemon.status()
        if status['status'] == 'running':
            print(f"   ✓ Daemon running on port {status.get('port', 8081)}")
            print(f"     PID: {status.get('pid', 'unknown')}")
        else:
            print("   ✗ Daemon not running")

    except Exception as e:
        print(f"   ✗ Error starting daemon: {e}")
        return 1

    # 6. Gateway is ready
    print("\n" + "=" * 40)
    print("Gateway is ready!")
    print(f"API endpoint: http://localhost:{daemon.port}/v1")
    print("\nYou can now:")
    print("- Send requests to the gateway")
    print("- Check usage with: tokligence usage")
    print("- Stop daemon with: tokligence-daemon stop")

    print("\nPress Ctrl+C to stop the gateway...")

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping gateway...")
        daemon.stop()
        print("✓ Gateway stopped")

    return 0


if __name__ == '__main__':
    sys.exit(main())