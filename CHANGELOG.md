# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflows for CI/CD
- Automated publishing to PyPI
- Version management scripts
- Contributing guidelines

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

[Unreleased]: https://github.com/tokligence/tokligence-gateway-python/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/tokligence/tokligence-gateway-python/releases/tag/v0.2.0