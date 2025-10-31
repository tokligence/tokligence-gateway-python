# Contributing to Tokligence Python Wrapper

Thank you for your interest in contributing to Tokligence! We welcome contributions from the community.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/tokligence-gateway-python
cd tokligence-gateway-python
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .[dev]
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tokligence

# Run specific test file
pytest tests/test_import.py
```

### Code Formatting

We use Black for code formatting:
```bash
black tokligence/ tests/
```

### Linting

We use Ruff for linting:
```bash
ruff check tokligence/ tests/
```

### Type Checking

We use mypy for type checking:
```bash
mypy tokligence/
```

## Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test them

3. Commit your changes:
```bash
git add .
git commit -m "feat: add new feature"
```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

## Submitting a Pull Request

1. Push your branch:
```bash
git push origin feature/your-feature-name
```

2. Open a Pull Request on GitHub

3. Describe your changes in the PR description

4. Wait for review and address feedback

## Version Management

### Manual Version Bump

```bash
# Bump patch version (0.2.0 -> 0.2.1)
python scripts/bump_version.py patch --commit --tag

# Bump minor version (0.2.0 -> 0.3.0)
python scripts/bump_version.py minor --commit --tag

# Bump major version (0.2.0 -> 1.0.0)
python scripts/bump_version.py major --commit --tag

# Set specific version
python scripts/bump_version.py 0.3.0 --commit --tag
```

### Automatic Release

Maintainers can use the GitHub Actions workflow to create releases:

1. Go to Actions → Version Management
2. Select version bump type
3. Check "Create GitHub release" and/or "Publish to PyPI"
4. Run workflow

## Building Go Binaries

The Python wrapper includes pre-compiled Go binaries. To update them:

1. Clone the main gateway repository:
```bash
git clone https://github.com/tokligence/tokligence-gateway ../tokligence-gateway
```

2. Build binaries:
```bash
cd ../tokligence-gateway
make dist-go
```

3. Copy to Python wrapper:
```bash
./scripts/build.sh
```

## Questions?

If you have questions, please:
1. Check existing issues
2. Create a new issue with the `question` label
3. Join our community discussions

Thank you for contributing! 🎉