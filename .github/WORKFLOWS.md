# GitHub Actions Workflows

This repository uses GitHub Actions for continuous integration and deployment.

## Workflows

### 🐳 Docker Image Publishing (`docker-publish.yml`)

**Triggers:**
- Push to `main` branch
- Version tags (`v*`)
- Manual workflow dispatch

**What it does:**
1. Builds multi-platform Docker images (amd64, arm64)
2. Publishes to:
   - **GitHub Container Registry**: `ghcr.io/unlink/immich-google-sync`
3. Tags images appropriately:
   - `latest` (main branch)
   - `v1.0.0` (semantic version from git tag)
   - `1.0` (major.minor)
   - `1` (major)
   - `main-sha123456` (branch + commit)

### ✅ Docker Image Testing (`docker-test.yml`)

**Triggers:**
- Pull requests to `main`
- Manual workflow dispatch

**What it does:**
1. Builds Docker image (test only, no push)
2. Starts container and verifies it runs
3. Checks health endpoint
4. Runs Python syntax validation

## Setup Instructions

### Required Secrets

Configure these in your GitHub repository settings (Settings → Secrets and variables → Actions):

#### For GitHub Container Registry (GHCR)
No additional secrets needed! Uses automatic `GITHUB_TOKEN`.

### First-Time Setup

1. **Enable GitHub Container Registry**
   - Push to main or create a tag
   - Image will appear at: `https://github.com/users/USERNAME/packages/container/immich-google-sync`

2. **Make Package Public** (Optional)
   - Go to package settings
   - Change visibility to Public
   - This allows anyone to pull without authentication

3. **Link Package to Repository** (Optional)
   - Go to package settings
   - Link to repository under "Connect repository"

## Usage

### Pull from GitHub Container Registry

```bash
# Latest version
docker pull ghcr.io/unlink/immich-google-sync:latest

# Specific version
docker pull ghcr.io/unlink/immich-google-sync:v1.0.0

# Run
docker run -d \
  -p 8080:8080 \
  -v ./data:/data \
  -e APP_SECRET_KEY=your-secret \
  ghcr.io/unlink/immich-google-sync:latest
```

### Update docker-compose.yml

```yaml
services:
  immich-gphotos-sync:
    image: ghcr.io/unlink/immich-google-sync:latest
    pull_policy: always
    # ... rest of config
```

## Creating a Release

### Automated Release Process

1. **Update version in CHANGELOG.md**
   ```bash
   git checkout main
   # Edit CHANGELOG.md with new version
   git add CHANGELOG.md
   git commit -m "chore: prepare release v1.0.0"
   git push
   ```

2. **Create and push tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Workflow automatically:**
   - Builds multi-platform images
   - Tags with version (v1.0.0, 1.0, 1, latest)
   - Pushes to registries
   - Creates release artifacts

### Manual Workflow Trigger

You can also manually trigger the workflow:
1. Go to Actions tab
2. Select "Build and Push Docker Image"
3. Click "Run workflow"
4. Select branch/tag
5. Click "Run workflow"

## Image Tags Explanation

| Tag | Description | Example |
|-----|-------------|---------|
| `latest` | Latest build from main branch | `latest` |
| `v{version}` | Specific semantic version | `v1.0.0` |
| `{major}.{minor}` | Major.minor version | `1.0` |
| `{major}` | Major version only | `1` |
| `main-{sha}` | Main branch + commit SHA | `main-abc1234` |
| `pr-{number}` | Pull request build | `pr-42` |

## Monitoring Builds

### View Workflow Runs
- Go to: https://github.com/Unlink/immich-google-mirroring/actions

### View Published Images
- **GHCR**: https://github.com/users/Unlink/packages/container/immich-google-sync

### Build Status Badge

Add to README.md:

```markdown
[![Docker Build](https://github.com/Unlink/immich-google-mirroring/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Unlink/immich-google-mirroring/actions/workflows/docker-publish.yml)
```

## Troubleshooting

### Build fails on push
- Check workflow logs in Actions tab
- Verify all secrets are set correctly
- Check DGITHUB_TOKEN has proper permissions
### Image not found after build
- Wait a few minutes for propagation
- Check package visibility (public vs private)
- Verify correct registry URL

### Permission denied on GHCR
- Ensure workflow has `packages: write` permission
- Check if organization/user settings allow package creation

### Multi-platform build fails
- This is expected on some runners
- Workflow uses QEMU for cross-platform builds
- May take longer for ARM builds

## Platform Support

Images are built for:
- ✅ `linux/amd64` (x86_64) - Intel/AMD processors
- ✅ `linux/arm64` (aarch64) - ARM processors (Raspberry Pi 4+, Apple Silicon via Docker)

Pull the image and Docker will automatically select the correct platform.

## Advanced Usage

### Use Specific Platform

```bash
# Force amd64
docker pull --platform linux/amd64 ghcr.io/unlink/immich-google-sync:latest

# Force arm64
docker pull --platform linux/arm64 ghcr.io/unlink/immich-google-sync:latest
```

### Build Locally

```bash
# Build for current platform
docker build -t immich-google-sync .

# Build for specific platform
docker buildx build --platform linux/amd64 -t immich-google-sync .

# Build multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -t immich-google-sync .
```

## Security

- Workflows use official GitHub Actions from verified publishers
- Docker images are scanned during build
- Only main branch and tags trigger pushes
- Pull requests only build, never push
- Uses short-lived `GITHUB_TOKEN` for GHCR authentication

## Cost Considerations

- **GitHub Actions**: Free for public repositories (2000 min/month for private)
- **GHCR**: Free for public packages
- **Docker Hub**: , unlimited pull
## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub](https://docs.docker.com/docker-hub/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
