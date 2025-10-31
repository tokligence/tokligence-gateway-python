# GitHub Actions Setup Guide

## Required Secrets

To enable automatic publishing, you need to configure the following secrets in your GitHub repository:

### 1. PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token:
   - Name: `tokligence-github-actions`
   - Scope: `Project: tokligence` (or entire account for first publish)
3. Copy the token (starts with `pypi-`)
4. Add to GitHub:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: paste your token

### 2. TestPyPI API Token (Optional)

1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Add to GitHub:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: paste your token

### 3. Trusted Publishing (Recommended)

Instead of using API tokens, you can set up trusted publishing:

1. Go to https://pypi.org/manage/project/tokligence/settings/publishing/
2. Add a new publisher:
   - Owner: `tokligence`
   - Repository: `tokligence-gateway-python`
   - Workflow: `publish.yml`
   - Environment: leave blank

This allows GitHub Actions to publish without storing tokens.

## Workflow Triggers

### CI Workflow
- **Automatic**: On every push to main and pull requests
- **Manual**: Actions → CI → Run workflow

### Publish Workflow
- **Automatic**: When creating a GitHub release or pushing tags (v*.*.*)
- **Manual**: Actions → Publish to PyPI → Run workflow

### Version Management
- **Manual only**: Actions → Version Management → Run workflow
- Options:
  - Bump version (patch/minor/major)
  - Create GitHub release
  - Publish to PyPI

## Usage Examples

### Creating a New Release

#### Option 1: Using GitHub UI
1. Go to Actions → Version Management
2. Select version type (e.g., "patch" for 0.2.0 → 0.2.1)
3. Check "Create GitHub release" ✅
4. Check "Publish to PyPI" ✅
5. Run workflow

#### Option 2: Using Command Line
```bash
# Bump version and create tag
python scripts/bump_version.py patch --commit --tag

# Push to trigger release
git push origin main
git push origin v0.2.1
```

#### Option 3: Manual Release
1. Create a release on GitHub
2. Tag format: `v0.2.1`
3. Publish workflow will trigger automatically

### Testing Changes

Before releasing:
```bash
# Run tests locally
pytest

# Check package build
python -m build
twine check dist/*

# Test on TestPyPI
Actions → Publish to PyPI → Run workflow → test_pypi: true
```

## Monitoring

### Check Workflow Status
- https://github.com/tokligence/tokligence-gateway-python/actions

### Check PyPI Package
- https://pypi.org/project/tokligence/

### View Download Statistics
- https://pypistats.org/packages/tokligence

## Troubleshooting

### Workflow Fails

1. Check Actions tab for error logs
2. Common issues:
   - Missing secrets
   - Version already exists on PyPI
   - Binary build failures

### Publishing Fails

1. Verify secrets are set correctly
2. Check token permissions
3. Ensure version number is incremented

### Binary Issues

The publish workflow automatically builds Go binaries. If this fails:
1. Check the tokligence-gateway repository is accessible
2. Verify Go version compatibility
3. Check Makefile targets exist

## Security Notes

- Never commit tokens to the repository
- Use repository secrets for sensitive data
- Consider using trusted publishing over API tokens
- Rotate tokens periodically

## Support

For issues with GitHub Actions:
- Create an issue with the `ci/cd` label
- Check the Actions logs and include relevant errors