#!/bin/bash
#
# Build script for tokligence Python package
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GATEWAY_ROOT="$(dirname "$PROJECT_ROOT")/tokligence-gateway"

echo "Building tokligence Python package..."
echo "Project root: $PROJECT_ROOT"
echo "Gateway root: $GATEWAY_ROOT"

# Check if gateway project exists
if [ ! -d "$GATEWAY_ROOT" ]; then
    echo "Error: Gateway project not found at $GATEWAY_ROOT"
    exit 1
fi

# Build Go binaries first
echo ""
echo "Step 1: Building Go binaries..."
cd "$GATEWAY_ROOT"

if [ ! -f "Makefile" ]; then
    echo "Error: Makefile not found in gateway project"
    exit 1
fi

# Build the binaries for all platforms
make clean-dist
make dist-go

# Check if binaries were built
if [ ! -d "dist" ] || [ -z "$(ls -A dist/*.exe dist/gateway-* dist/gatewayd-* 2>/dev/null)" ]; then
    echo "Error: No binaries found in dist/ directory"
    exit 1
fi

echo "✓ Go binaries built successfully"

# Return to Python project
cd "$PROJECT_ROOT"

# Clean previous builds
echo ""
echo "Step 2: Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Create binaries directory
mkdir -p tokligence/binaries

# Copy binaries from gateway project
echo ""
echo "Step 3: Copying binaries..."
cp -v "$GATEWAY_ROOT"/dist/gateway-*-linux-amd64 tokligence/binaries/gateway-linux-amd64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gateway-*-linux-arm64 tokligence/binaries/gateway-linux-arm64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gateway-*-darwin-amd64 tokligence/binaries/gateway-darwin-amd64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gateway-*-darwin-arm64 tokligence/binaries/gateway-darwin-arm64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gateway-*-windows-amd64.exe tokligence/binaries/gateway-windows-amd64.exe 2>/dev/null || true

cp -v "$GATEWAY_ROOT"/dist/gatewayd-*-linux-amd64 tokligence/binaries/gatewayd-linux-amd64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gatewayd-*-linux-arm64 tokligence/binaries/gatewayd-linux-arm64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gatewayd-*-darwin-amd64 tokligence/binaries/gatewayd-darwin-amd64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gatewayd-*-darwin-arm64 tokligence/binaries/gatewayd-darwin-arm64 2>/dev/null || true
cp -v "$GATEWAY_ROOT"/dist/gatewayd-*-windows-amd64.exe tokligence/binaries/gatewayd-windows-amd64.exe 2>/dev/null || true

# Make binaries executable
chmod +x tokligence/binaries/* 2>/dev/null || true

# Count copied binaries
BINARY_COUNT=$(ls -1 tokligence/binaries/ | wc -l)
echo "✓ Copied $BINARY_COUNT binaries"

# Build Python package
echo ""
echo "Step 4: Building Python package..."

# Install build dependencies if needed
pip install --quiet --upgrade pip build

# Build the package
python -m build

# Check if wheel was created
if [ ! -f dist/*.whl ]; then
    echo "Error: Wheel package not created"
    exit 1
fi

echo ""
echo "✓ Build complete!"
echo ""
echo "Package files:"
ls -lh dist/

echo ""
echo "To install locally for testing:"
echo "  pip install dist/*.whl"
echo ""
echo "To publish to PyPI:"
echo "  python -m twine upload dist/*"