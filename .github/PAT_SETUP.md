# Setting up Personal Access Token (PAT)

If the default GITHUB_TOKEN doesn't work, you can use a Personal Access Token.

## Creating a PAT

1. Go to GitHub Settings:
   - Click your profile picture → Settings
   - Or go to: https://github.com/settings/tokens

2. Generate new token (classic):
   - Click "Developer settings" (bottom of sidebar)
   - Click "Personal access tokens" → "Tokens (classic)"
   - Click "Generate new token" → "Generate new token (classic)"

3. Configure token:
   - **Note**: `tokligence-gateway-python-actions`
   - **Expiration**: 90 days (or longer)
   - **Select scopes**:
     - ✅ `repo` (all)
     - ✅ `workflow`
     - ✅ `write:packages` (if publishing packages)

4. Generate and copy token

5. Add to repository secrets:
   - Go to: https://github.com/tokligence/tokligence-gateway-python/settings/secrets/actions
   - Click "New repository secret"
   - **Name**: `PAT_TOKEN`
   - **Value**: paste your token

## Update workflow to use PAT

If needed, change the checkout step in `.github/workflows/version.yml`:

```yaml
    - uses: actions/checkout@v4
      with:
        token: ${{ secrets.PAT_TOKEN }}  # Instead of GITHUB_TOKEN
        fetch-depth: 0
```

## Security Notes

- Keep the token secure
- Rotate regularly
- Use minimal required permissions
- Consider using GitHub App tokens for production