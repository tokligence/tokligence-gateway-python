# Tokligence - Multi-platform LLM Gateway

[![CI Status](https://github.com/tokligence/tokligence-gateway-python/actions/workflows/ci.yml/badge.svg)](https://github.com/tokligence/tokligence-gateway-python/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/tokligence)](https://pypi.org/project/tokligence/)
[![Python Version](https://img.shields.io/pypi/pyversions/tokligence)](https://pypi.org/project/tokligence/)
[![Downloads](https://img.shields.io/pypi/dm/tokligence)](https://pypi.org/project/tokligence/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **[Tokligence Gateway](https://github.com/tokligence/tokligence-gateway)** - A multi-platform LLM gateway with unified OpenAI, Anthropic, and Google Gemini APIs.

This package provides a convenient Python interface to the Tokligence Gateway, bundling pre-compiled Go binaries for easy installation via pip or uv.

**New in v0.3.4:** AI-powered configuration assistant via `tgw chat` command!

## 🚀 Quick Start

```bash
# Install
pip install tokligence

# Initialize and start
tokligence init
tokligence-daemon start --background

# Your gateway is now running at http://localhost:8081
```

Now use it with any OpenAI-compatible client:
```python
import openai
openai.api_base = "http://localhost:8081/v1"
# Use your favorite LLM through the gateway!
```

## Features

### Installation & Deployment
- 🚀 **Zero Dependencies on Go** - Pre-compiled binaries included
- 🌍 **Cross-Platform** - Works on Linux, macOS, and Windows
- 🔧 **Simple CLI** - Intuitive command-line interface
- 🐍 **Pythonic API** - Native Python wrappers for gateway operations
- 📦 **Easy Installation** - Just `pip install tokligence`

### Gateway Capabilities (v0.3.4)
- 🔄 **Multi-Provider Support** - OpenAI, Anthropic, and Google Gemini
- 🌐 **Dual Protocol Support** - OpenAI and Anthropic native APIs simultaneously
- 🛠️ **Advanced Tool Calling** - Full function calling with automatic translation
- 🎯 **Intelligent Routing** - Auto, passthrough, or translation work modes
- 📊 **Production Features** - Prometheus metrics, rate limiting, health checks
- 🗄️ **Database Support** - SQLite and PostgreSQL with connection pooling
- ⚡ **High Performance** - 9.6x faster than LiteLLM with sub-100ms latency

## Installation

### Via pip

```bash
pip install tokligence
```

### Via uv (recommended for faster installation)

```bash
uv add tokligence
```

### From source

```bash
git clone https://github.com/tokligence/tokligence-gateway
cd tokligence-gateway/python  # 或者你的实际路径
pip install -e .
```

## Quick Start

### 1. Initialize Configuration

```bash
# Initialize gateway configuration
tokligence init

# Or with custom config path
tokligence --config ~/myconfig.yaml init
```

### 2. Start the Gateway Daemon

```bash
# Start in foreground
tokligence-daemon start

# Start in background
tokligence-daemon start --background

# Start on custom port (or use short alias)
tokligenced start --port 8080
```

### 3. Create Users and API Keys

```bash
# Create a user
tokligence user create alice --email alice@example.com

# List users
tokligence user list

# Create API key for user
tokligence apikey create <user-id> --name "Production Key"
```

### 4. Use the Gateway

Once running, the gateway provides an OpenAI-compatible API:

```python
import openai

# Point to your local gateway
openai.api_base = "http://localhost:8081/v1"
openai.api_key = "your-api-key"

# Use as normal
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## 🤖 AI Configuration Assistant (New!)

Get AI-powered help with configuration and troubleshooting:

```bash
# Install with chat support
pip install "tokligence[chat]"

# Start the AI assistant
tgw chat

# Or specify a model
tgw chat --model gpt-4
tgw chat --model claude-sonnet-4.5
```

The assistant can:
- ✨ Answer questions about configuration
- 🛠️ Execute configuration commands
- 📚 Search official documentation
- 🔍 Troubleshoot issues
- 🔐 Safely handle sensitive data (masks API keys automatically)

**Supported LLM Providers:**
- OpenAI API (set `TOKLIGENCE_OPENAI_API_KEY`)
- Anthropic API (set `TOKLIGENCE_ANTHROPIC_API_KEY`)
- Google Gemini API (set `TOKLIGENCE_GOOGLE_API_KEY`)
- Local LLMs via Ollama, vLLM, or LM Studio (no API key needed)

## Python API

### Basic Usage

```python
from tokligence import Gateway, Daemon

# Initialize gateway
gateway = Gateway()
gateway.init()

# Create a user
user = gateway.create_user("alice", email="alice@example.com")
print(f"Created user: {user['id']}")

# List users
users = gateway.list_users()
for user in users:
    print(f"User: {user['username']} ({user['email']})")

# Start daemon
daemon = Daemon(port=8081)
daemon.start(background=True)

# Check status
status = daemon.status()
print(f"Daemon status: {status['status']}")

# Stop daemon
daemon.stop()
```

### Configuration Management

```python
from tokligence import Config, load_config

# Load configuration
config = load_config()

# Get values
port = config.get('gateway.port', 8081)
auth_enabled = config.get('gateway.auth.enabled', False)

# Set values
config.set('gateway.port', 8080)
config.set('providers.openai.api_key', 'sk-...')

# Update multiple values
config.update({
    'gateway': {
        'port': 8080,
        'auth': {'enabled': True}
    }
})

# Save configuration
config.save()

# Convert to environment variables
env_vars = config.to_env_vars()
# Returns: {'TOKLIGENCE_GATEWAY_PORT': '8080', ...}
```

### Advanced Example - Team Gateway Setup

```python
from tokligence import Gateway, Daemon, Config
import time

def setup_team_gateway():
    """Set up a gateway for team use with authentication."""

    # Configure gateway
    config = Config()
    config.update({
        'gateway': {
            'port': 8081,
            'auth': {
                'enabled': True,
                'type': 'api_key'
            }
        },
        'providers': {
            'openai': {
                'enabled': True,
                'api_key': 'your-openai-key'
            },
            'anthropic': {
                'enabled': True,
                'api_key': 'your-anthropic-key'
            }
        }
    })
    config.save()

    # Initialize gateway
    gateway = Gateway()
    gateway.init()

    # Create team users
    team_members = [
        ('alice', 'alice@team.com'),
        ('bob', 'bob@team.com'),
        ('charlie', 'charlie@team.com')
    ]

    for username, email in team_members:
        user = gateway.create_user(username, email)
        api_key = gateway.create_api_key(
            user['id'],
            name=f"{username}'s API Key"
        )
        print(f"User: {username}")
        print(f"  ID: {user['id']}")
        print(f"  API Key: {api_key['key']}")
        print()

    # Start daemon
    daemon = Daemon(port=8081)
    print("Starting gateway daemon...")
    daemon.start(background=True)

    # Wait for startup
    time.sleep(2)

    # Check status
    status = daemon.status()
    if status['status'] == 'running':
        print(f"✅ Gateway running on port {status['port']}")
        print(f"   PID: {status['pid']}")
    else:
        print("❌ Failed to start gateway")

    return daemon

if __name__ == '__main__':
    daemon = setup_team_gateway()

    # Run until interrupted
    try:
        print("\nGateway is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping gateway...")
        daemon.stop()
```

## CLI Commands

### Gateway CLI

```bash
# Initialize configuration
tokligence init

# User management
tokligence user create <username> [--email <email>]
tokligence user list [--json]

# API key management
tokligence apikey create <user-id> [--name <name>]

# Usage statistics
tokligence usage [--user <user-id>] [--json]

# Version info
tokligence version
```

### Daemon CLI

```bash
# Start daemon (use either command)
tokligence-daemon start [--port <port>] [--background]
tokligenced start [--port <port>] [--background]

# Stop daemon
tokligence-daemon stop

# Restart daemon
tokligence-daemon restart [--port <port>]

# Check status
tokligence-daemon status
```

## Configuration

Configuration can be managed through:

1. **Configuration file** (`~/.config/tokligence/config.yaml`)
2. **Environment variables** (prefix: `TOKLIGENCE_`)
3. **Command-line arguments**

### Example Configuration

```yaml
gateway:
  host: localhost
  port: 8081
  auth:
    enabled: true
    type: api_key
  logging:
    level: info
    file: /var/log/tokgateway.log

database:
  type: sqlite
  path: ~/.config/tokligence/gateway.db

providers:
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    base_url: https://api.openai.com/v1
    models:
      - gpt-4
      - gpt-3.5-turbo

  anthropic:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY}
    base_url: https://api.anthropic.com
    models:
      - claude-3-opus
      - claude-3-sonnet
```

### Environment Variables

All configuration options can be set via environment variables:

```bash
export TOKLIGENCE_GATEWAY_PORT=8080
export TOKLIGENCE_GATEWAY_AUTH_ENABLED=true
export TOKLIGENCE_PROVIDERS_OPENAI_API_KEY=sk-...
export TOKLIGENCE_PROVIDERS_ANTHROPIC_API_KEY=sk-ant-...
```

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/tokligence/tokligence-gateway
cd tokligence-gateway/python  # 或者你的实际路径

# Build the package (requires Go binaries)
./scripts/build.sh

# Install in development mode
pip install -e .

# Run tests
pytest
```

### Publishing

```bash
# Build package
./scripts/build.sh

# Upload to TestPyPI
./scripts/publish.sh --test

# Upload to PyPI
./scripts/publish.sh
```

## Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | amd64 | ✅ Supported |
| Linux | arm64 | ✅ Supported |
| macOS | amd64 (Intel) | ✅ Supported |
| macOS | arm64 (Apple Silicon) | ✅ Supported |
| Windows | amd64 | ✅ Supported |

## Troubleshooting

### Binary not found error

If you encounter "Binary not found" errors, ensure:
1. The package was installed correctly
2. Your platform is supported (see table above)
3. Try reinstalling: `pip install --force-reinstall tokligence`

### Permission denied errors

On Unix-like systems, the binaries should be automatically made executable. If you encounter permission issues:

```bash
# Find the package location
python -c "import tokligence; print(tokligence.__file__)"

# Make binaries executable
chmod +x /path/to/tokligence/binaries/*
```

### Gateway fails to start

Check if the port is already in use:

```bash
# Check port 8081
lsof -i :8081  # macOS/Linux
netstat -ano | findstr :8081  # Windows
```

## Contributing

Contributions are welcome! Please see the main [Tokligence Gateway](https://github.com/tokligence/tokligence-gateway) repository for contribution guidelines.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/tokligence/tokligence-gateway/issues)
- **Documentation**: [Tokligence Gateway Docs](https://github.com/tokligence/tokligence-gateway)
- **Email**: cs@tokligence.ai

## Related Projects

- [Tokligence Gateway](https://github.com/tokligence/tokligence-gateway) - The core Go implementation
- [Tokligence Marketplace](https://tokligence.ai) - Token marketplace integration