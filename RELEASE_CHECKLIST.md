# Release Checklist for tokgateway

## Pre-release checks

- [ ] Version number updated in `pyproject.toml`
- [ ] Version number updated in `tokgateway/__init__.py`
- [ ] README.md is up to date
- [ ] All tests pass
- [ ] Package builds successfully
- [ ] Binary files are included in the package
- [ ] `twine check dist/*` passes

## Build process

```bash
# 1. Clean old builds
rm -rf dist/ build/ *.egg-info

# 2. Build Go binaries
./scripts/build.sh

# 3. Or just build Python package if binaries already exist
python -m build

# 4. Check the package
twine check dist/*
```

## Publishing

### First time setup

1. Create PyPI account at https://pypi.org/
2. Generate API token from account settings
3. Save token securely

### Publish to TestPyPI (optional)

```bash
# Upload
python -m twine upload --repository testpypi dist/*

# Test install
pip install -i https://test.pypi.org/simple/ tokgateway
```

### Publish to PyPI

```bash
# Using token
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YOUR_TOKEN python -m twine upload dist/*

# Or with .pypirc configured
python -m twine upload dist/*
```

## Post-release

- [ ] Verify on PyPI: https://pypi.org/project/tokgateway/
- [ ] Test installation: `pip install tokgateway`
- [ ] Create GitHub release
- [ ] Update documentation if needed

## Troubleshooting

### "Binary not found" after installation
- Ensure all platform binaries are included
- Check file permissions in the package

### "Package exists" error
- Increment version number
- Delete old uploads from PyPI if testing

### Authentication failed
- Ensure using `__token__` as username
- Check token starts with `pypi-`
- Verify token has correct scope