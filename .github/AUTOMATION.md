# Automation Workflows

This repository uses GitHub Actions to automate the release process and keep in sync with the main [tokligence-gateway](https://github.com/tokligence/tokligence-gateway) repository.

## Workflows

### 1. Sync with Gateway Release (`sync-release.yml`)

**Purpose**: Automatically detect new Gateway releases and publish updated Python package.

**Trigger**:
- Runs every 3 hours via cron schedule (`0 */3 * * *`)
- Can be manually triggered via `workflow_dispatch`

**What it does**:
1. Checks for new releases in `tokligence/tokligence-gateway`
2. If new version found:
   - Updates `pyproject.toml` and `tokligence/__init__.py` with new version
   - Clones Gateway repo at the new version tag
   - Syncs documentation to `tokligence/knowledge/`
   - Updates `CHANGELOG.md` with new entry
   - Runs tests to ensure everything works
   - Commits changes and pushes to main
   - Creates and pushes git tag (e.g., `v0.3.5`)
   - Tag push triggers the publish workflow automatically

**Manual trigger**:
```bash
gh workflow run sync-release.yml
# Or with specific version
gh workflow run sync-release.yml --field version=0.3.5
```

### 2. Publish to PyPI (`publish.yml`)

**Purpose**: Build and publish the Python package to PyPI.

**Trigger**:
- Git tag push (e.g., `git push origin v0.3.4`)
- GitHub release creation
- Manual `workflow_dispatch`

**What it does**:
1. Downloads precompiled binaries from Gateway release
2. Sets up Python environment
3. Builds Python wheel package
4. Validates package with twine
5. Publishes to PyPI using Trusted Publishing (OIDC)
6. Creates GitHub Release with release notes

**Manual trigger**:
```bash
# Option 1: Via tag (recommended)
git tag v0.3.5 -m "Release v0.3.5"
git push origin v0.3.5

# Option 2: Via workflow dispatch
gh workflow run publish.yml --field version=0.3.5 --field test_pypi=false
```

### 3. CI (`ci.yml`)

**Purpose**: Run tests on every push and pull request.

**Trigger**: Push to any branch, pull requests

**What it does**:
- Runs pytest test suite
- Validates code quality
- Ensures package imports correctly

## Release Flow

### Automatic (Recommended)

The sync workflow handles everything automatically:

```
Gateway releases v0.3.5
         ↓
Sync workflow detects new version (runs every 3h)
         ↓
Updates version, docs, CHANGELOG
         ↓
Runs tests
         ↓
Commits and pushes changes
         ↓
Creates and pushes tag v0.3.5
         ↓
Publish workflow triggered by tag
         ↓
Downloads binaries from Gateway v0.3.5
         ↓
Builds and publishes to PyPI
         ↓
Creates GitHub Release
```

### Manual

If you need to trigger a release manually:

```bash
# 1. Ensure version is updated in pyproject.toml and __init__.py

# 2. Create and push tag
git tag v0.3.5 -m "Release v0.3.5"
git push origin v0.3.5

# 3. Publish workflow runs automatically

# Or use workflow dispatch:
gh workflow run publish.yml --field version=0.3.5 --field test_pypi=false
```

## Configuration

### PyPI Trusted Publishing

This project uses PyPI's Trusted Publishing (OIDC) for secure, token-less publishing.

**Configuration** (already set up):
- PyPI Project: `tokligence`
- GitHub Owner: `tokligence`
- Repository: `tokligence-gateway-python`
- Workflow: `publish.yml`
- Environment: (none)

See: https://pypi.org/manage/project/tokligence/settings/publishing/

### Permissions

The workflows require the following GitHub token permissions:
- `contents: write` - For creating releases and pushing commits/tags
- `id-token: write` - For PyPI OIDC authentication

These are configured in each workflow file.

## Monitoring

### Check Sync Status

```bash
# List recent workflow runs
gh run list --workflow=sync-release.yml --limit 5

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### Check Publish Status

```bash
# List recent publishes
gh run list --workflow=publish.yml --limit 5

# Check if version is on PyPI
pip index versions tokligence
```

### Next Scheduled Sync

The sync workflow runs every 3 hours. To see when it last ran:

```bash
gh run list --workflow=sync-release.yml --limit 1
```

## Troubleshooting

### Sync workflow skipped update

Check the logs to see if versions matched:
```bash
gh run view <run-id> --log | grep "No update needed"
```

### Publish failed

Common issues:
1. **Trusted publishing not configured**: Ensure PyPI trusted publisher is set up
2. **Binaries not found**: Ensure Gateway release has all binary assets
3. **Version already exists**: PyPI won't allow republishing same version

### Manual recovery

If automatic sync fails, you can manually trigger:
```bash
# Sync with specific version
gh workflow run sync-release.yml --field version=0.3.5

# Or manually update and publish
./scripts/bump_version.sh 0.3.5
git tag v0.3.5 -m "Release v0.3.5"
git push origin main v0.3.5
```

## Development

### Testing Sync Workflow Locally

```bash
# Simulate version check
LATEST=$(gh api repos/tokligence/tokligence-gateway/releases/latest --jq '.tag_name')
CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Latest: $LATEST, Current: v$CURRENT"

# Sync docs manually
python scripts/sync_docs.py
```

### Testing Publish Workflow

Use TestPyPI first:
```bash
gh workflow run publish.yml --field version=0.3.5-test --field test_pypi=true
```

Then test install:
```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple tokligence==0.3.5-test
```
