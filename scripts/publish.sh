#!/bin/bash
#
# Publish script for tokligence Python package
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Publishing tokligence to PyPI..."

# Check for required tools
if ! command -v twine &> /dev/null; then
    echo "Installing twine..."
    pip install --upgrade twine
fi

# Check for dist directory
if [ ! -d "dist" ]; then
    echo "Error: dist/ directory not found. Run build.sh first."
    exit 1
fi

# Check for credentials
if [ -z "$TWINE_USERNAME" ] && [ -z "$TWINE_PASSWORD" ]; then
    echo "Warning: TWINE_USERNAME and TWINE_PASSWORD not set"
    echo "You can set them as environment variables or enter them when prompted"
    echo ""
fi

# Optionally upload to TestPyPI first
if [ "$1" == "--test" ]; then
    echo "Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✓ Uploaded to TestPyPI"
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ tokligence"
else
    echo "Uploading to PyPI..."
    python -m twine upload dist/*
    echo ""
    echo "✓ Uploaded to PyPI"
    echo "Install with:"
    echo "  pip install tokligence"
fi