"""
Download script for d-sync
Downloads encrypted/compressed files from Discord CDN and reconstructs them
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import sys
from datetime import datetime

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    Logger, EncryptionManager, CompressionManager, HashManager,
    D_SYNCED_DIR, FILES_JSON, MAX_PARTITION_SIZE, DOWNLOAD_LOG_FILE
)

logger = Logger(__name__)


class D_SyncDownload:
    """Main download manager for d-sync"""

    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.compression_manager = CompressionManager()
        self.files_metadata: Dict[str, Dict] = {}
        self._load_files_metadata()

    def _load_files_metadata(self):
        """Load files metadata from JSON"""
        if not FILES_JSON.exists():
            logger.error(f"Files metadata not found: {FILES_JSON}")
            logger.info("You need to upload files first using d_sync_upload.py")
            return

        try:
            with open(FILES_JSON, 'r') as f:
                data = json.load(f)
                self.files_metadata = data.get('files', {})
                logger.info(f"Loaded metadata for {len(self.files_metadata)} files")
        except json.JSONDecodeError as e:
            logger.error(f"Could not parse files.json: {e}")

    def _download_chunk(self, cdn_url: str) -> Optional[bytes]:
        """Download a chunk from Discord CDN"""
        try:
            response = requests.get(cdn_url, timeout=60)
            response.raise_for_status()
            logger.debug(f"Downloaded chunk from {cdn_url}")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download chunk: {e}")
            return None

    def _log_response(self, filename: str, status: str, message: str):
        """Log download response"""
        try:
            DOWNLOAD_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DOWNLOAD_LOG_FILE, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n[{timestamp}] {filename}\n")
                f.write(f"Status: {status}\n")
                f.write(f"Message: {message}\n")
                f.write("="*80 + "\n")
        except Exception as e:
            logger.error(f"Error logging response: {e}")

    def download_file(self, file_path: str) -> bool:
        """Download and reconstruct a file"""
        logger.info(f"Downloading file: {file_path}")

        if file_path not in self.files_metadata:
            logger.error(f"File not found in metadata: {file_path}")
            return False

        try:
            metadata = self.files_metadata[file_path]

            # Check if file is marked as deleted
            if metadata.get('deleted', False):
                logger.warning(f"File is marked as deleted: {file_path}")
                return False

            chunks = metadata.get('chunks', [])
            if not chunks:
                logger.error(f"No chunks found for file: {file_path}")
                return False

            # Download all chunks
            downloaded_chunks = {}
            for chunk_info in chunks:
                chunk_index = chunk_info.get('chunk_index')
                cdn_url = chunk_info.get('cdn_url')

                if not cdn_url:
                    logger.error(f"No CDN URL for chunk {chunk_index}")
                    return False

                chunk_data = self._download_chunk(cdn_url)
                if not chunk_data:
                    logger.error(f"Failed to download chunk {chunk_index}")
                    return False

                # Verify chunk hash
                chunk_hash = HashManager.calculate_chunk_hash(chunk_data)
                expected_hash = chunk_info.get('chunk_hash')

                if chunk_hash != expected_hash:
                    logger.error(
                        f"Chunk hash mismatch for {file_path} chunk {chunk_index}"
                    )
                    return False

                downloaded_chunks[chunk_index] = chunk_data
                logger.debug(f"Downloaded and verified chunk {chunk_index}")

            # Reconstruct file
            reconstructed_data = b''
            for i in range(len(downloaded_chunks)):
                reconstructed_data += downloaded_chunks[i]

            # Decrypt if encrypted
            if metadata.get('encrypted', False):
                reconstructed_data = self.encryption_manager.decrypt_data(
                    reconstructed_data
                )
                logger.debug(f"Decrypted file: {file_path}")

            # Decompress if compressed
            if metadata.get('compressed', False):
                reconstructed_data = self.compression_manager.decompress_data(
                    reconstructed_data
                )
                logger.debug(f"Decompressed file: {file_path}")

            # Verify file hash
            file_hash = HashManager.calculate_data_hash(reconstructed_data)
            expected_file_hash = metadata.get('file_hash')

            if file_hash != expected_file_hash:
                logger.error(f"File hash mismatch for {file_path}")
                logger.error(f"Expected: {expected_file_hash}, Got: {file_hash}")
                return False

            # Write to file
            output_path = D_SYNCED_DIR / file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(reconstructed_data)

            logger.info(f"Successfully downloaded and reconstructed: {file_path}")
            self._log_response(file_path, "SUCCESS", "File downloaded and reconstructed")
            return True

        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}", exc_info=True)
            self._log_response(file_path, "ERROR", str(e))
            return False

    def download_all_files(self) -> int:
        """Download all files from metadata"""
        logger.info("Starting download of all files")

        if not self.files_metadata:
            logger.warning("No files in metadata")
            return 0

        success_count = 0
        for file_path in self.files_metadata.keys():
            # Skip deleted files
            if self.files_metadata[file_path].get('deleted', False):
                logger.info(f"Skipping deleted file: {file_path}")
                continue

            if self.download_file(file_path):
                success_count += 1

        logger.info(f"Downloaded {success_count}/{len(self.files_metadata)} files")
        return success_count

    def download_specific_file(self, file_path: str) -> bool:
        """Download a specific file"""
        return self.download_file(file_path)

    def list_available_files(self) -> List[str]:
        """List all available files in metadata"""
        available = []
        for file_path, metadata in self.files_metadata.items():
            if not metadata.get('deleted', False):
                available.append(file_path)
        return available


def main():
    """Main entry point"""
    logger.info("Starting d-sync download service")

    download = D_SyncDownload()

    # List available files
    available_files = download.list_available_files()
    if not available_files:
        logger.warning("No files available for download")
        return

    logger.info(f"Available files ({len(available_files)}):")
    for i, file_path in enumerate(available_files, 1):
        logger.info(f"  {i}. {file_path}")

    # Download all files
    logger.info("\nDownloading all files...")
    success_count = download.download_all_files()

    logger.info(f"\nDownload complete: {success_count} files successfully downloaded")
    logger.info(f"Files are restored to: {D_SYNCED_DIR}")


if __name__ == '__main__':
    main()
