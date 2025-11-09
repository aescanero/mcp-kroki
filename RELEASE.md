# Release Process

This document describes how to create and publish new releases of mcp-kroki.

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (v1.0.0 -> v2.0.0): Incompatible API changes
- **MINOR** version (v1.0.0 -> v1.1.0): Add functionality in a backward compatible manner
- **PATCH** version (v1.0.0 -> v1.0.1): Backward compatible bug fixes

## Creating a Release

### 1. Prepare the Release

Before creating a release, ensure:
- All tests pass
- Documentation is up to date
- CHANGELOG is updated with new changes
- You're on the `main` branch with latest changes

### 2. Create and Push a Version Tag

The recommended way to create a release is using **git tags** with the format `v*.*.*`:

```bash
# Ensure you're on the main branch and up to date
git checkout main
git pull origin main

# Create a new tag (example: v1.0.0)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

**Tag Format:**
- Always prefix with `v` (e.g., `v1.0.0`, `v1.2.3`)
- Use three numbers separated by dots: `v<major>.<minor>.<patch>`
- Examples: `v1.0.0`, `v1.2.3`, `v2.0.0`

### 3. Automated Build Process

Once you push a tag matching `v*.*.*`, the GitHub Action will automatically:

1. ✅ Build the Docker image
2. ✅ Tag the image with multiple versions:
   - `aescanero/mcp-kroki:1.0.0` (full version)
   - `aescanero/mcp-kroki:1.0` (major.minor)
   - `aescanero/mcp-kroki:1` (major)
   - `aescanero/mcp-kroki:latest`
3. ✅ Push to Docker Hub
4. ✅ Build for multiple platforms (linux/amd64, linux/arm64)

### 4. Create GitHub Release (Optional but Recommended)

After the Docker image is published, create a GitHub release:

```bash
# Using GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0 - Release Title" \
  --notes "## Changes

- Feature 1
- Feature 2
- Bug fix 3
"

# Or use the GitHub web interface:
# Go to: https://github.com/aescanero/mcp-kroki/releases/new
```

**Or via GitHub Web Interface:**
1. Go to your repository on GitHub
2. Click on "Releases" in the right sidebar
3. Click "Draft a new release"
4. Select the tag you just pushed (v1.0.0)
5. Add a release title and description
6. Click "Publish release"

## Release Examples

### Patch Release (Bug Fix)
```bash
# Current version: v1.0.0
# New version: v1.0.1

git checkout main
git pull origin main
git tag -a v1.0.1 -m "Release v1.0.1 - Fix critical bug in diagram generation"
git push origin v1.0.1
```

### Minor Release (New Features)
```bash
# Current version: v1.0.1
# New version: v1.1.0

git checkout main
git pull origin main
git tag -a v1.1.0 -m "Release v1.1.0 - Add support for new diagram types"
git push origin v1.1.0
```

### Major Release (Breaking Changes)
```bash
# Current version: v1.1.0
# New version: v2.0.0

git checkout main
git pull origin main
git tag -a v2.0.0 -m "Release v2.0.0 - Major API changes"
git push origin v2.0.0
```

## Docker Image Tags

After each release, the following Docker image tags are available:

| Tag Pattern | Example | Description |
|------------|---------|-------------|
| `latest` | `aescanero/mcp-kroki:latest` | Always points to the most recent release |
| `<major>` | `aescanero/mcp-kroki:1` | Latest release in major version 1 |
| `<major>.<minor>` | `aescanero/mcp-kroki:1.0` | Latest patch in version 1.0 |
| `<major>.<minor>.<patch>` | `aescanero/mcp-kroki:1.0.0` | Specific release version |

## Docker Hub Repository

All images are published to: **https://hub.docker.com/r/aescanero/mcp-kroki**

## Rollback a Release

If you need to rollback or delete a tag:

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
```

**Note:** If Docker images were already pushed, you'll need to manually remove them from Docker Hub or mark them as deprecated.

## Viewing Release History

```bash
# List all tags
git tag -l

# Show tag information
git show v1.0.0

# View releases on GitHub
gh release list
```

## Prerequisites

Before creating releases, ensure:

1. **Docker Hub Token**: The `DOCKER_TOKEN` secret is configured in GitHub repository settings
2. **Permissions**: You have write access to the repository
3. **Clean State**: Working directory is clean (`git status` shows no uncommitted changes)

## Troubleshooting

### Build Failed
- Check GitHub Actions logs: `https://github.com/aescanero/mcp-kroki/actions`
- Verify DOCKER_TOKEN secret is set correctly
- Ensure Dockerfile builds locally: `docker build -t test .`

### Tag Already Exists
```bash
# If you need to move a tag to a different commit
git tag -f v1.0.0
git push origin v1.0.0 --force
```

### Docker Hub Authentication Failed
- Verify DOCKER_TOKEN in GitHub Settings → Secrets → Actions
- Ensure the token has write permissions
- Check token hasn't expired

## Best Practices

1. ✅ Always test builds locally before tagging
2. ✅ Update CHANGELOG.md before each release
3. ✅ Use annotated tags (`-a` flag) with descriptive messages
4. ✅ Follow semantic versioning strictly
5. ✅ Create GitHub releases with detailed release notes
6. ✅ Test the Docker image after publication
7. ✅ Never force-push to main branch
