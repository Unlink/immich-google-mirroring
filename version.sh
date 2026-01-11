#!/bin/bash
# Version management script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VERSION_FILE="$PROJECT_ROOT/app/__version__.py"
CHANGELOG_FILE="$PROJECT_ROOT/CHANGELOG.md"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  show              Show current version"
    echo "  bump <type>       Bump version (major|minor|patch)"
    echo "  set <version>     Set specific version (X.Y.Z)"
    echo "  release <version> Create a release (update files, git tag, etc.)"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 show"
    echo "  $0 bump patch"
    echo "  $0 set 1.1.0"
    echo "  $0 release 1.0.1"
}

function get_current_version() {
    grep '__version__ = ' "$VERSION_FILE" | sed -E 's/.*"([^"]+)".*/\1/'
}

function show_version() {
    local version=$(get_current_version)
    echo -e "${BLUE}Immich Google Photos Mirroring - Version ${GREEN}$version${NC}"
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

function update_version_file() {
    local new_version=$1
    local major=$(echo $new_version | cut -d. -f1)
    local minor=$(echo $new_version | cut -d. -f2)
    local patch=$(echo $new_version | cut -d. -f3)
    
    # Update version file (works on macOS and Linux)
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" "$VERSION_FILE"
    sed -i.bak "s/__version_info__ = ([^)]*)/__version_info__ = ($major, $minor, $patch)/" "$VERSION_FILE"
    rm -f "$VERSION_FILE.bak"
    
    echo -e "${GREEN}✓${NC} Updated $VERSION_FILE"
}

function update_docker_compose() {
    local new_version=$1
    sed -i.bak "s/VERSION: .*/VERSION: $new_version/" "$DOCKER_COMPOSE_FILE"
    sed -i.bak "s|image: ghcr.io/unlink/immich-google-sync:[^ ]*|image: ghcr.io/unlink/immich-google-sync:$new_version|" "$DOCKER_COMPOSE_FILE"
    rm -f "$DOCKER_COMPOSE_FILE.bak"
    
    echo -e "${GREEN}✓${NC} Updated $DOCKER_COMPOSE_FILE"
}

function bump_version() {
    local bump_type=$1
    local current=$(get_current_version)
    local major=$(echo $current | cut -d. -f1)
    local minor=$(echo $current | cut -d. -f2)
    local patch=$(echo $current | cut -d. -f3)
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo -e "${RED}Error: Unknown bump type: $bump_type${NC}"
            echo "Use: major, minor, or patch"
            return 1
            ;;
    esac
    
    local new_version="$major.$minor.$patch"
    set_version "$new_version"
}

function set_version() {
    local new_version=$1
    
    if ! validate_version "$new_version"; then
        return 1
    fi
    
    local current=$(get_current_version)
    if [ "$current" = "$new_version" ]; then
        echo -e "${YELLOW}Version is already $new_version${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Updating version from ${YELLOW}$current${BLUE} to ${YELLOW}$new_version${NC}"
    
    update_version_file "$new_version"
    update_docker_compose "$new_version"
    
    echo -e "${GREEN}✓ Version updated to $new_version${NC}"
}

function create_release() {
    local version=$1
    
    if ! validate_version "$version"; then
        return 1
    fi
    
    set_version "$version"
    
    # Check if git is available
    if command -v git &> /dev/null; then
        echo -e "${BLUE}Creating git release...${NC}"
        
        git add "$VERSION_FILE" "$DOCKER_COMPOSE_FILE" "$CHANGELOG_FILE" 2>/dev/null || true
        git commit -m "chore(release): v$version" 2>/dev/null || true
        git tag -a "v$version" -m "Release version $version" 2>/dev/null || true
        
        echo -e "${GREEN}✓ Git tag created: v$version${NC}"
        echo -e "${BLUE}Push with: git push origin main && git push origin v$version${NC}"
    else
        echo -e "${YELLOW}Git not found. Please manually commit and tag the release.${NC}"
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    show_version
    exit 0
fi

case $1 in
    show)
        show_version
        ;;
    bump)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: bump type not specified${NC}"
            show_usage
            exit 1
        fi
        bump_version "$2"
        ;;
    set)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: version not specified${NC}"
            show_usage
            exit 1
        fi
        set_version "$2"
        ;;
    release)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: version not specified${NC}"
            show_usage
            exit 1
        fi
        create_release "$2"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command: $1${NC}"
        show_usage
        exit 1
        ;;
esac
