"""
Build hooks for including Go binaries in the Python package
"""

import os
import shutil
import stat
import urllib.request
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Any


class CustomBuildHook:
    """Custom build hook to include Go binaries in the wheel."""

    BINARY_URLS = {
        # These URLs would point to your GitHub releases or build artifacts
        # Format: platform-arch: url
        'linux-amd64': 'https://github.com/tokligence/tokligence-gateway/releases/download/{version}/gateway-{version}-linux-amd64.tar.gz',
        'linux-arm64': 'https://github.com/tokligence/tokligence-gateway/releases/download/{version}/gateway-{version}-linux-arm64.tar.gz',
        'darwin-amd64': 'https://github.com/tokligence/tokligence-gateway/releases/download/{version}/gateway-{version}-darwin-amd64.tar.gz',
        'darwin-arm64': 'https://github.com/tokligence/tokligence-gateway/releases/download/{version}/gateway-{version}-darwin-arm64.tar.gz',
        'windows-amd64': 'https://github.com/tokligence/tokligence-gateway/releases/download/{version}/gateway-{version}-windows-amd64.zip',
    }

    def __init__(self, *args, **kwargs):
        self.version = os.environ.get('TOKGATEWAY_VERSION', 'v0.2.0')
        self.binaries_dir = Path('tokgateway/binaries')

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize the build hook."""
        self.binaries_dir.mkdir(parents=True, exist_ok=True)

        # First, try to copy from local build directory
        if self.copy_local_binaries():
            print("✓ Using local binaries from ../tokligence-gateway/dist/")
            return

        # Otherwise, download from releases
        print(f"Downloading binaries for version {self.version}...")
        self.download_binaries()

    def copy_local_binaries(self) -> bool:
        """
        Copy binaries from local tokligence-gateway build.

        Returns:
            True if local binaries were found and copied
        """
        local_dist = Path('../tokligence-gateway/dist')
        if not local_dist.exists():
            return False

        copied = False
        binary_names = ['gateway', 'gatewayd']

        # Map of platform names
        platform_map = {
            'linux-amd64': 'linux-amd64',
            'linux-arm64': 'linux-arm64',
            'darwin-amd64': 'darwin-amd64',
            'darwin-arm64': 'darwin-arm64',
            'windows-amd64': 'windows-amd64',
        }

        for platform, file_platform in platform_map.items():
            for binary_name in binary_names:
                # Look for binary file
                pattern = f"{binary_name}-*-{file_platform}"
                if platform.startswith('windows'):
                    pattern += '.exe'

                for src_file in local_dist.glob(pattern):
                    # Determine destination filename
                    if platform.startswith('windows'):
                        dst_name = f"{binary_name}-{platform}.exe"
                    else:
                        dst_name = f"{binary_name}-{platform}"

                    dst_file = self.binaries_dir / dst_name

                    print(f"  Copying {src_file.name} -> {dst_file.name}")
                    shutil.copy2(src_file, dst_file)

                    # Make executable on Unix-like systems
                    if not platform.startswith('windows'):
                        st = os.stat(dst_file)
                        os.chmod(dst_file, st.st_mode | stat.S_IEXEC)

                    copied = True

        return copied

    def download_binaries(self) -> None:
        """Download binaries from GitHub releases."""
        for platform, url_template in self.BINARY_URLS.items():
            url = url_template.format(version=self.version)
            filename = url.split('/')[-1]
            download_path = self.binaries_dir / filename

            print(f"  Downloading {platform} binary from {url}")

            try:
                urllib.request.urlretrieve(url, download_path)

                # Extract the archive
                if filename.endswith('.tar.gz'):
                    with tarfile.open(download_path, 'r:gz') as tar:
                        tar.extractall(self.binaries_dir)
                elif filename.endswith('.zip'):
                    with zipfile.ZipFile(download_path, 'r') as zip_ref:
                        zip_ref.extractall(self.binaries_dir)

                # Clean up archive
                download_path.unlink()

                # Rename binaries to expected format
                self.rename_binaries(platform)

            except Exception as e:
                print(f"  Warning: Could not download {platform} binary: {e}")

    def rename_binaries(self, platform: str) -> None:
        """Rename extracted binaries to expected format."""
        binary_names = ['gateway', 'gatewayd']

        for binary_name in binary_names:
            # Find the extracted binary
            for file in self.binaries_dir.glob(f"{binary_name}*"):
                if file.is_file() and platform in str(file):
                    # Determine new name
                    if platform.startswith('windows'):
                        new_name = f"{binary_name}-{platform}.exe"
                    else:
                        new_name = f"{binary_name}-{platform}"

                    new_path = self.binaries_dir / new_name

                    # Rename if needed
                    if file.name != new_name:
                        file.rename(new_path)
                        print(f"    Renamed {file.name} -> {new_name}")

                    # Make executable on Unix-like systems
                    if not platform.startswith('windows'):
                        st = os.stat(new_path)
                        os.chmod(new_path, st.st_mode | stat.S_IEXEC)

                    break

    def finalize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Finalize the build."""
        # Verify binaries are present
        binary_count = len(list(self.binaries_dir.glob('*')))
        print(f"✓ Build complete with {binary_count} binaries")


# Entry point for hatchling
def hatch_register_custom_hook():
    return CustomBuildHook