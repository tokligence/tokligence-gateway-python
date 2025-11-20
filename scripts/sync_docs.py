#!/usr/bin/env python3
"""
Documentation Sync Script

Syncs documentation from the Go repository to the Python package's knowledge base.
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
GO_REPO_PATH = Path(sys.argv[1] if len(sys.argv) > 1 else SCRIPT_DIR.parent.parent / "tokligence-gateway")
KNOWLEDGE_DIR = SCRIPT_DIR.parent / "tokligence" / "knowledge"

def hash_file(file_path):
    """Calculate MD5 hash of file content"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_git_info(repo_path):
    """Get git information from Go repository"""
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_path,
            encoding='utf-8'
        ).strip()

        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            cwd=repo_path,
            encoding='utf-8'
        ).strip().replace('v', '', 1)  # Remove 'v' prefix if present

        return {'commit': commit, 'version': tag}
    except Exception as e:
        print(f'⚠️  Failed to get git info: {e}')
        return {'commit': 'unknown', 'version': 'unknown'}

def sync_docs():
    """Copy documentation files"""
    print('📚 Syncing documentation from Go repository...\n')

    # Check if Go repo exists
    if not GO_REPO_PATH.exists():
        print(f'❌ Go repository not found at: {GO_REPO_PATH}')
        print('Please provide the correct path as an argument:')
        print('  python scripts/sync_docs.py /path/to/tokligence-gateway')
        sys.exit(1)

    # Create knowledge directory if it doesn't exist
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    # Files to sync (relative to Go repo root)
    files_to_sync = [
        'README.md',
        'docs/QUICK_START.md',
        'docs/USER_GUIDE.md',
        'docs/configuration_guide.md'
    ]

    synced_files = []
    file_hashes = {}

    # Copy each file
    for file in files_to_sync:
        source_path = GO_REPO_PATH / file
        file_name = Path(file).name
        dest_path = KNOWLEDGE_DIR / file_name

        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            file_hash = hash_file(dest_path)
            file_hashes[file_name] = file_hash
            synced_files.append({
                'name': file_name,
                'source': file,
                'hash': file_hash[:8]
            })
            print(f'✓ Copied {file} -> {file_name}')
        else:
            print(f'⚠️  Skipped {file} (not found)')

    # Get git information
    git_info = get_git_info(GO_REPO_PATH)

    # Generate metadata
    meta = {
        'version': git_info['version'],
        'commit': git_info['commit'][:8],
        'syncedAt': datetime.utcnow().isoformat() + 'Z',
        'files': file_hashes,
        'links': {
            'github': 'https://github.com/tokligence/tokligence-gateway',
            'pypi': 'https://pypi.org/project/tokligence/',
            'website': 'https://tokligence.ai',
            'wiki': 'https://github.com/tokligence/tokligence-gateway/wiki'
        }
    }

    # Write metadata
    meta_path = KNOWLEDGE_DIR / '_meta.json'
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print('\n📋 Sync Summary:')
    print(f"  Version: {meta['version']}")
    print(f"  Commit: {meta['commit']}")
    print(f"  Files synced: {len(synced_files)}")
    print(f"  Synced at: {meta['syncedAt']}")

    print('\n✓ Documentation sync completed!\n')

    return {
        'success': True,
        'meta': meta,
        'files': synced_files
    }

if __name__ == '__main__':
    try:
        sync_docs()
    except Exception as e:
        print(f'\n❌ Sync failed: {e}')
        sys.exit(1)
