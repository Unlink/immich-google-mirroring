#!/bin/bash
# Complete release automation script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_usage() {
    echo "Usage: $0 <version> [--dry-run]"
    echo ""
    echo "Arguments:"
    echo "  version     Version in format X.Y.Z (e.g., 1.1.0)"
    echo "  --dry-run   Show what would be done without making changes"
    echo ""
    echo "Example:"
    echo "  $0 1.1.0"
    echo "  $0 1.1.0 --dry-run"
}

function validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid version format: $version${NC}"
        echo "Expected format: X.Y.Z (e.g., 1.0.1)"
        return 1
    fi
    return 0
}

function check_git_status() {
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git not found${NC}"
        return 1
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}Warning: Working directory has uncommitted changes${NC}"
        git status
        return 1
    fi
    
    return 0
}

function edit_changelog() {
    echo -e "${BLUE}Opening CHANGELOG.md for editing...${NC}"
    if [ -n "$EDITOR" ]; then
        $EDITOR "$PROJECT_ROOT/CHANGELOG.md"
    elif command -v nano &> /dev/null; then
        nano "$PROJECT_ROOT/CHANGELOG.md"
    elif command -v vi &> /dev/null; then
        vi "$PROJECT_ROOT/CHANGELOG.md"
    else
        echo -e "${YELLOW}Could not open editor. Please manually edit CHANGELOG.md${NC}"
        return 1
    fi
    return 0
}

function update_version() {
    local version=$1
    local dry_run=$2
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${BLUE}[DRY-RUN] Would update version to: $version${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Updating version to $version...${NC}"
    "$PROJECT_ROOT/version.sh" set "$version"
    echo -e "${GREEN}✓ Version updated${NC}"
}

function commit_changes() {
    local version=$1
    local dry_run=$2
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${BLUE}[DRY-RUN] Would commit with message: chore(release): v$version${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Committing changes...${NC}"
    git add app/__version__.py CHANGELOG.md docker-compose.yml
    git commit -m "chore(release): v$version"
    echo -e "${GREEN}✓ Changes committed${NC}"
}

function create_git_tag() {
    local version=$1
    local dry_run=$2
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${BLUE}[DRY-RUN] Would create tag: v$version${NC}"
        echo -e "${BLUE}[DRY-RUN] Would push: git push origin main && git push origin v$version${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Creating git tag...${NC}"
    git tag -a "v$version" -m "Release version $version"
    echo -e "${GREEN}✓ Git tag created: v$version${NC}"
}

function push_changes() {
    local version=$1
    local dry_run=$2
    
    if [ "$dry_run" = "true" ]; then
        echo -e "${BLUE}[DRY-RUN] Would push changes and tags${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Pushing changes and tags...${NC}"
    echo -e "${YELLOW}This will trigger GitHub Actions workflows${NC}"
    git push origin main
    git push origin "v$version"
    echo -e "${GREEN}✓ Pushed to GitHub${NC}"
}

function show_summary() {
    local version=$1
    local dry_run=$2
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}[DRY-RUN] Release Summary for v$version${NC}"
    else
        echo -e "${GREEN}Release v$version completed!${NC}"
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "What happened:"
    echo "  1. Updated version to $version"
    echo "  2. Updated CHANGELOG.md with release notes"
    echo "  3. Committed changes"
    echo "  4. Created git tag v$version"
    echo "  5. Pushed to GitHub"
    echo ""
    echo "GitHub Actions will automatically:"
    echo "  1. Build Docker image for linux/amd64 and linux/arm64"
    echo "  2. Push image to ghcr.io/<owner>/immich-google-sync:$version"
    echo "  3. Push image to ghcr.io/<owner>/immich-google-sync:latest"
    echo "  4. Create GitHub Release with changelog"
    echo ""
    echo "Check progress at:"
    echo "  - Actions: https://github.com/<owner>/immich-google-mirroring/actions"
    echo "  - Releases: https://github.com/<owner>/immich-google-mirroring/releases"
    echo "  - Packages: https://ghcr.io/<owner>/immich-google-sync"
    echo ""
}

# Main script
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

VERSION=$1
DRY_RUN="false"

if [ "$2" = "--dry-run" ]; then
    DRY_RUN="true"
    echo -e "${YELLOW}Running in DRY-RUN mode (no changes will be made)${NC}"
    echo ""
fi

if ! validate_version "$VERSION"; then
    exit 1
fi

if [ "$DRY_RUN" != "true" ]; then
    if ! check_git_status; then
        echo -e "${RED}Please commit all changes before releasing${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Starting release process for v$VERSION...${NC}"
echo ""

# Step 1: Edit changelog
if [ "$DRY_RUN" != "true" ]; then
    echo "Step 1: Update CHANGELOG.md"
    if ! edit_changelog; then
        echo -e "${RED}Changelog edit cancelled${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Changelog updated${NC}"
    echo ""
fi

# Step 2: Update version
echo "Step 2: Update version"
update_version "$VERSION" "$DRY_RUN"
echo ""

# Step 3: Commit changes
echo "Step 3: Commit changes"
commit_changes "$VERSION" "$DRY_RUN"
echo ""

# Step 4: Create git tag
echo "Step 4: Create git tag"
create_git_tag "$VERSION" "$DRY_RUN"
echo ""

# Step 5: Push changes
echo "Step 5: Push to GitHub"
push_changes "$VERSION" "$DRY_RUN"
echo ""

# Summary
show_summary "$VERSION" "$DRY_RUN"
