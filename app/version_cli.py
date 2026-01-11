"""
CLI utility for version management
"""
import sys
import re
from pathlib import Path
from app import __version__

def print_version():
    """Print current version"""
    print(f"Immich Google Photos Mirroring - Version {__version__}")


def update_version(new_version: str) -> bool:
    """Update version in all relevant files"""
    # Validate version format (semantic versioning)
    if not re.match(r'^\d+\.\d+\.\d+', new_version):
        print(f"Error: Invalid version format. Expected format: X.Y.Z (e.g., 1.0.1)")
        return False
    
    # Get the version file path
    version_file = Path(__file__).parent / "__version__.py"
    
    try:
        # Read current content
        content = version_file.read_text()
        
        # Extract version info
        major, minor, patch = new_version.split('.')[:3]
        
        # Update __version__
        content = re.sub(
            r'__version__ = "[^"]*"',
            f'__version__ = "{new_version}"',
            content
        )
        
        # Update __version_info__
        content = re.sub(
            r'__version_info__ = \([^)]*\)',
            f'__version_info__ = ({major}, {minor}, {patch})',
            content
        )
        
        # Write updated content
        version_file.write_text(content)
        
        print(f"✓ Updated version to {new_version}")
        return True
        
    except Exception as e:
        print(f"Error updating version: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_version()
    elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Usage: python -m app.version_cli [command]")
        print("Commands:")
        print("  (no args)     Print current version")
        print("  update X.Y.Z  Update version to X.Y.Z")
    elif sys.argv[1] == "update" and len(sys.argv) > 2:
        if update_version(sys.argv[2]):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)
