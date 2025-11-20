# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.4] - 2024-11-20

### Added
- **AI Configuration Assistant** - Interactive `tgw chat` command for AI-powered configuration help
  - Supports OpenAI, Anthropic, Google Gemini, and local LLMs (Ollama, vLLM, LM Studio)
  - Automatic endpoint detection and selection
  - Tool calling for executing configuration commands
  - Documentation search with embedded knowledge base
  - Sensitive data masking for API keys and secrets
- PostgreSQL ledger support with connection pooling
- Database connection pool management for better performance
- Security updates (upgraded glob to fix CVE-2025-64756)
- `tgw` command alias for shorter CLI commands
- Comprehensive test suite for chat functionality (26 tests, 85%+ coverage)

### Improved
- Better database connection handling
- Enhanced stability for high-traffic scenarios
- Updated package description to reflect multi-protocol support

### Fixed
- Database connection pool parameters in SQLite ledger tests
- Sensitive API key logging removed

## [0.3.3] - 2024-11-15

### Added
- Google Gemini API integration with pass-through proxy
- Support for Gemini API endpoints
- Gemini configuration documentation

### Security
- Fixed sensitive api_key_id exposure in logs

## [0.3.2] - 2024-11-12

### Added
- Comprehensive performance benchmark framework
- Prometheus metrics endpoint for monitoring
- Production-ready rate limiting with distributed support
- Enhanced health check with dependency monitoring

### Performance
- Benchmark results showing 9.6x faster throughput vs LiteLLM
- Sub-100ms P99 latency under high load
- 0% error rate under stress testing

## [0.3.1] - 2024-11-08

### Added
- Centralized version management in internal/version package
- Enhanced health check endpoints
- Better routing and token counting logs

### Improved
- Model metadata loader with per-model capability caps
- Better configuration management

## [0.3.0] - 2024-11-05

### Added
- Advanced OpenAI ↔ Anthropic translation capabilities
- Streaming support for chat-to-anthropic translation
- Beta header handling for Anthropic API
- Configurable duplicate tool detection
- Docker deployment support (personal and team editions)
- Tool adapter for Codex compatibility
- Unified TOKLIGENCE_WORK_MODE configuration

### Improved
- Enhanced Anthropic bridging and translation
- Model-cap aware clamping
- Better tool call handling and validation

### Fixed
- Docker entrypoint path corrections
- Database persistence for team edition
- Codex-compatible duplicate tool call detection

## [0.2.1] - 2024-11-01

### Added
- GitHub Actions workflows for CI/CD
  - Automated testing across Python 3.8-3.12
  - Cross-platform testing (Linux, macOS, Windows)
  - Automated PyPI publishing
- Version management automation
  - `bump_version.py` script for version updates
  - GitHub Actions version workflow
- Contributing guidelines (CONTRIBUTING.md)
- GitHub Actions setup documentation
- CI status badges in README

### Improved
- Better error handling in CLI commands
- More robust binary detection across platforms
- Documentation updates with workflow instructions

### Fixed
- GitHub Actions permissions for tag pushing
- CI workflow dependency installation

## [0.2.0] - 2024-11-01

### Added
- Initial release of Tokligence Python wrapper
- Core Python wrapper modules (Gateway, Daemon, CLI)
- Command-line interface using Click
- Configuration management system
- Support for Linux, macOS, and Windows
- Bundled pre-compiled Go binaries
- Basic import and configuration tests
- Comprehensive documentation and examples
- Build and publish automation scripts

### Features
- `tokligence` CLI command for gateway management
- `tokligence-daemon` command for running the daemon
- Python API for programmatic control
- Automatic platform detection and binary selection
- Configuration file management (YAML/JSON)
- Environment variable support

### Supported Platforms
- Linux (amd64, arm64)
- macOS (Intel, Apple Silicon)
- Windows (amd64)

[Unreleased]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.3.4...HEAD
[0.3.4]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/tokligence/tokligence-gateway-python/releases/tag/v0.2.0