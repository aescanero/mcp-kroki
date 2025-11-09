# Setting up DOCKER_TOKEN for GitHub Actions

This document explains how to configure the `DOCKER_TOKEN` secret for automated Docker Hub publishing.

## Prerequisites

- Docker Hub account: https://hub.docker.com/
- Write access to the GitHub repository
- Repository: https://hub.docker.com/r/aescanero/mcp-kroki

## Step 1: Create Docker Hub Access Token

1. Log in to Docker Hub: https://hub.docker.com/
2. Click on your profile icon in the top right
3. Select **Account Settings**
4. Navigate to **Security** tab
5. Click **New Access Token**
6. Configure the token:
   - **Description**: `GitHub Actions - mcp-kroki`
   - **Access permissions**: Select **Read, Write, Delete** (or **Read & Write** if available)
7. Click **Generate**
8. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

## Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository: https://github.com/aescanero/mcp-kroki
2. Click on **Settings** tab
3. In the left sidebar, navigate to **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Configure the secret:
   - **Name**: `DOCKER_TOKEN`
   - **Value**: Paste the Docker Hub access token from Step 1
6. Click **Add secret**

## Step 3: Verify Configuration

The secret should now appear in the list of repository secrets as:
- Name: `DOCKER_TOKEN`
- Updated: (current date)

You can test the configuration by creating a test tag:

```bash
git tag -a v0.0.1-test -m "Test release"
git push origin v0.0.1-test
```

Then check the Actions tab to see if the workflow runs successfully:
https://github.com/aescanero/mcp-kroki/actions

## Troubleshooting

### "Invalid username/password" error
- Verify the token was copied correctly without extra spaces
- Ensure the token hasn't expired
- Check that the token has write permissions

### "Repository not found" error
- Verify the repository name in the workflow file matches your Docker Hub repository
- Ensure the username in the workflow file is correct (should be `aescanero`)

### Token expiration
Docker Hub access tokens don't expire by default, but if you set an expiration:
1. Create a new token following Step 1
2. Update the GitHub secret following Step 2

## Security Best Practices

1. ✅ Never commit tokens to git
2. ✅ Use repository secrets, not environment variables in code
3. ✅ Rotate tokens periodically (every 6-12 months)
4. ✅ Delete tokens that are no longer needed
5. ✅ Use minimal required permissions for tokens

## Revoking a Token

If a token is compromised:

1. Go to Docker Hub → Account Settings → Security
2. Find the token in the list
3. Click **Delete** next to the token
4. Create a new token and update the GitHub secret

## Additional Resources

- Docker Hub Access Tokens: https://docs.docker.com/docker-hub/access-tokens/
- GitHub Actions Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- GitHub Actions Workflow: `.github/workflows/docker-publish.yml`
