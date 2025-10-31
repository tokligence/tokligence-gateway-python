#!/usr/bin/env python3
"""
Version bump utility for tokligence package
"""

import re
import sys
import argparse
from pathlib import Path


def get_current_version(file_path, pattern):
    """Get current version from file."""
    content = Path(file_path).read_text()
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def update_version(file_path, pattern, new_version):
    """Update version in file."""
    content = Path(file_path).read_text()
    new_content = re.sub(pattern, f'\\g<0>'.replace('(.*?)', new_version), content)
    Path(file_path).write_text(new_content)


def bump_version(version_type='patch'):
    """Bump version number."""
    # Files to update
    files = [
        ('pyproject.toml', r'version = "(.*?)"'),
        ('tokligence/__init__.py', r'__version__ = "(.*?)"'),
    ]

    # Get current version
    current = get_current_version(files[0][0], files[0][1])
    if not current:
        print("Could not find current version")
        return False

    # Parse version
    parts = current.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    # Bump version
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        # Custom version
        new_version = version_type

    if version_type in ['major', 'minor', 'patch']:
        new_version = f"{major}.{minor}.{patch}"

    print(f"Bumping version: {current} → {new_version}")

    # Update all files
    for file_path, pattern in files:
        update_version(file_path, pattern, new_version)
        print(f"  Updated {file_path}")

    return new_version


def main():
    parser = argparse.ArgumentParser(description='Bump version')
    parser.add_argument(
        'version',
        nargs='?',
        default='patch',
        help='Version type (major, minor, patch) or specific version (e.g., 0.3.0)'
    )
    parser.add_argument('--tag', action='store_true', help='Create git tag')
    parser.add_argument('--commit', action='store_true', help='Commit changes')

    args = parser.parse_args()

    new_version = bump_version(args.version)
    if not new_version:
        sys.exit(1)

    if args.commit:
        import subprocess
        subprocess.run(['git', 'add', 'pyproject.toml', 'tokligence/__init__.py'])
        subprocess.run(['git', 'commit', '-m', f'chore: bump version to {new_version}'])
        print(f"Committed version {new_version}")

    if args.tag:
        import subprocess
        tag = f"v{new_version}"
        subprocess.run(['git', 'tag', tag])
        print(f"Created tag {tag}")
        print(f"Push with: git push origin main {tag}")


if __name__ == '__main__':
    main()