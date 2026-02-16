"""
Main upload script for d-sync
Monitors d-synced folder and uploads files to Discord
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    Logger, EncryptionManager, CompressionManager, HashManager,
    WebhookManager, D_SYNCED_DIR, FILES_JSON, FOLDERS_JSON,
    MAX_PARTITION_SIZE, UPLOAD_LOG_FILE, FILES_JSON_UPLOAD_META
)

logger = Logger(__name__)


class FileMetadata:
    """Represents metadata for a file"""

    def __init__(self, file_path: Path, compressed: bool = False, encrypted: bool = False):
        self.file_path = file_path
        self.relative_path = file_path.relative_to(D_SYNCED_DIR)
        self.file_hash = HashManager.calculate_file_hash(file_path)
        self.file_size = file_path.stat().st_size
        self.date_created = datetime.fromtimestamp(
            file_path.stat().st_ctime
        ).isoformat()
        self.file_type = file_path.suffix
        self.compressed = compressed
        self.encrypted = encrypted
        self.chunks = []  # List of {chunk_index, hash, cdn_url}
        self.deleted = False

    def to_dict(self):
        return {
            'file_path': str(self.relative_path),
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'date_created': self.date_created,
            'file_type': self.file_type,
            'compressed': self.compressed,
            'encrypted': self.encrypted,
            'chunks': self.chunks,
            'deleted': self.deleted
        }


class FolderMetadata:
    """Represents metadata for a folder"""

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.relative_path = folder_path.relative_to(D_SYNCED_DIR)
        self.date_created = datetime.fromtimestamp(
            folder_path.stat().st_ctime
        ).isoformat()
        self.file_count = sum(1 for _ in folder_path.rglob('*') if _.is_file())
        self.folder_count = sum(1 for _ in folder_path.rglob('*') if _.is_dir())
        self.cdn_url = None

    def to_dict(self):
        return {
            'folder_path': str(self.relative_path),
            'date_created': self.date_created,
            'file_count': self.file_count,
            'folder_count': self.folder_count,
            'cdn_url': self.cdn_url
        }


class D_SyncUpload:
    """Main upload manager for d-sync"""

    def __init__(self):
        self.webhook_manager = WebhookManager()
        self.encryption_manager = EncryptionManager()
        self.compression_manager = CompressionManager()
        self.files_metadata: Dict[str, Dict] = {}
        self.folders_metadata: Dict[str, Dict] = {}
        self.tracked_files = set()
        self._load_existing_metadata()

    def _load_existing_metadata(self):
        """Load existing metadata from JSON files"""
        if FILES_JSON.exists():
            try:
                with open(FILES_JSON, 'r') as f:
                    data = json.load(f)
                    self.files_metadata = data.get('files', {})
                    logger.info("Loaded existing files metadata")
            except json.JSONDecodeError:
                logger.warning("Could not parse files.json, starting fresh")

        if FOLDERS_JSON.exists():
            try:
                with open(FOLDERS_JSON, 'r') as f:
                    data = json.load(f)
                    self.folders_metadata = data.get('folders', {})
                    logger.info("Loaded existing folders metadata")
            except json.JSONDecodeError:
                logger.warning("Could not parse folders.json, starting fresh")

    def _save_files_metadata(self):
        """Save files metadata to JSON"""
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'files': self.files_metadata
        }
        FILES_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(FILES_JSON, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved files metadata to {FILES_JSON}")
        # Attempt to upload or update files.json on remote storage
        try:
            self._ensure_files_json_remote()
        except Exception as e:
            logger.debug(f"Could not ensure remote files.json: {e}")

    def _ensure_files_json_remote(self):
        """Upload files.json once and PATCH the remote message on updates.
        Stores remote info in `FILES_JSON_UPLOAD_META`.
        """
        # Choose a webhook to use
        webhook_url = self.webhook_manager.get_random_webhook()
        if not webhook_url:
            logger.warning("No webhook available to upload files.json")
            return

        # Read local files.json bytes
        try:
            with open(FILES_JSON, 'rb') as f:
                data_bytes = f.read()
        except Exception as e:
            logger.error(f"Failed to read {FILES_JSON} for remote upload: {e}")
            return

        prev_meta = None
        if FILES_JSON_UPLOAD_META.exists():
            try:
                with open(FILES_JSON_UPLOAD_META, 'r') as mf:
                    prev_meta = json.load(mf)
            except Exception:
                prev_meta = None

        # If we have previous meta, try to PATCH the message first
        if prev_meta:
            prev_webhook = prev_meta.get('webhook_url')
            prev_msg_id = prev_meta.get('message_id')
            if prev_webhook and prev_msg_id:
                logger.info(f"Attempting to PATCH existing files.json message {prev_msg_id}")
                resp = self.webhook_manager.patch_message(prev_webhook, prev_msg_id, data=data_bytes, filename='files.json')
                if resp:
                    # Update meta
                    new_meta = {
                        'webhook_url': prev_webhook,
                        'message_id': resp.get('id'),
                        'cdn_url': self.webhook_manager.extract_cdn_url(resp),
                        'last_updated': datetime.now().isoformat()
                    }
                    with open(FILES_JSON_UPLOAD_META, 'w') as mf:
                        json.dump(new_meta, mf, indent=2)
                    logger.info("Patched remote files.json message successfully")
                    return
                else:
                    logger.info("Patching files.json failed; will upload a new message")

        # Upload a new message with files.json
        logger.info("Uploading files.json to remote storage")
        resp = self.webhook_manager.upload_bytes(webhook_url, data_bytes, 'files.json')
        if resp:
            msg_id = resp.get('id')
            cdn = self.webhook_manager.extract_cdn_url(resp)
            new_meta = {
                'webhook_url': webhook_url,
                'message_id': msg_id,
                'cdn_url': cdn,
                'last_updated': datetime.now().isoformat()
            }
            with open(FILES_JSON_UPLOAD_META, 'w') as mf:
                json.dump(new_meta, mf, indent=2)
            logger.info(f"Uploaded files.json as message {msg_id}")
            # If there was a previous message, try to delete it for cleanup
            if prev_meta and prev_meta.get('webhook_url') and prev_meta.get('message_id'):
                try:
                    self.webhook_manager.delete_message(prev_meta.get('webhook_url'), prev_meta.get('message_id'))
                    logger.info(f"Deleted previous files.json message {prev_meta.get('message_id')}")
                except Exception:
                    logger.debug("Failed to delete previous files.json message")
        else:
            logger.error("Failed to upload files.json to remote storage")

    def _save_folders_metadata(self):
        """Save folders metadata to JSON"""
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'folders': self.folders_metadata
        }
        FOLDERS_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(FOLDERS_JSON, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved folders metadata to {FOLDERS_JSON}")

    def _partition_file(self, file_data: bytes) -> List[bytes]:
        """Partition file data into chunks of MAX_PARTITION_SIZE"""
        chunks = []
        for i in range(0, len(file_data), int(MAX_PARTITION_SIZE)):
            chunk = file_data[i:i + int(MAX_PARTITION_SIZE)]
            chunks.append(chunk)
        logger.debug(f"Partitioned data into {len(chunks)} chunks")
        return chunks

    def _process_file(self, file_path: Path) -> bool:
        """Process and upload a single file"""
        logger.info(f"Processing file: {file_path}")

        try:
            # Check if already uploaded
            relative_path = str(file_path.relative_to(D_SYNCED_DIR))
            if relative_path in self.files_metadata:
                logger.info(f"File already tracked: {relative_path}")
                return True

            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Compress if enabled
            compressed = False
            if len(file_data) > 1024 * 100:  # Compress files > 100KB
                file_data = self.compression_manager.compress_data(file_data)
                compressed = True
                logger.debug(f"Compressed file: {file_path}")

            # Encrypt if enabled
            encrypted = False
            if True:  # Encryption enabled by default
                file_data = self.encryption_manager.encrypt_data(file_data)
                encrypted = True
                logger.debug(f"Encrypted file: {file_path}")

            # Partition file
            chunks = self._partition_file(file_data)

            # Create metadata
            metadata = FileMetadata(file_path, compressed, encrypted)

            # Upload chunks
            for chunk_index, chunk_data in enumerate(chunks):
                chunk_hash = HashManager.calculate_chunk_hash(chunk_data)
                webhook_url = self.webhook_manager.get_random_webhook()

                if not webhook_url:
                    logger.error("No webhooks available")
                    return False

                # Create temporary file for upload
                chunk_filename = f"{metadata.file_hash}_chunk_{chunk_index}.bin"
                response = self.webhook_manager.upload_bytes(
                    webhook_url, chunk_data, chunk_filename
                )

                if response:
                    cdn_url = self.webhook_manager.extract_cdn_url(response)
                    if cdn_url:
                        metadata.chunks.append({
                            'chunk_index': chunk_index,
                            'chunk_hash': chunk_hash,
                            'webhook_url': webhook_url,
                            'cdn_url': cdn_url
                        })
                        logger.info(f"Uploaded chunk {chunk_index}: {chunk_filename}")

                        # Save response to log
                        self._log_response(chunk_filename, response)
                    else:
                        logger.warning(f"No CDN URL in response for chunk {chunk_index}")
                else:
                    logger.error(f"Failed to upload chunk {chunk_index}")
                    return False

            # Save metadata
            self.files_metadata[relative_path] = metadata.to_dict()
            self._save_files_metadata()

            logger.info(f"Successfully uploaded file: {relative_path}")
            self.tracked_files.add(relative_path)
            return True

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            return False

    def _process_folder(self, folder_path: Path):
        """Process a folder and create metadata"""
        logger.info(f"Processing folder: {folder_path}")

        try:
            relative_path = str(folder_path.relative_to(D_SYNCED_DIR))

            # Check if already processed
            if relative_path in self.folders_metadata:
                logger.info(f"Folder already tracked: {relative_path}")
                return

            # Create metadata
            metadata = FolderMetadata(folder_path)

            # Create folder metadata JSON
            folder_json_path = folder_path / "folder_metadata.json"
            folder_json_data = metadata.to_dict()

            # Upload folder metadata
            webhook_url = self.webhook_manager.get_random_webhook()
            if webhook_url:
                response = self.webhook_manager.upload_bytes(
                    webhook_url,
                    json.dumps(folder_json_data).encode(),
                    f"folder_metadata_{relative_path.replace(chr(92), '_')}.json"
                )

                if response:
                    cdn_url = self.webhook_manager.extract_cdn_url(response)
                    metadata.cdn_url = cdn_url
                    logger.info(f"Uploaded folder metadata: {relative_path}")

            self.folders_metadata[relative_path] = metadata.to_dict()
            self._save_folders_metadata()
            logger.info(f"Successfully processed folder: {relative_path}")

        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}", exc_info=True)

    def _log_response(self, filename: str, response: Dict):
        """Log webhook response"""
        try:
            UPLOAD_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UPLOAD_LOG_FILE, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n[{timestamp}] {filename}\n")
                f.write(json.dumps(response, indent=2))
                f.write("\n" + "="*80 + "\n")
        except Exception as e:
            logger.error(f"Error logging response: {e}")

    def scan_directory(self):
        """Scan d-synced directory for new files and folders"""
        logger.info("Scanning directory for changes...")

        if not D_SYNCED_DIR.exists():
            logger.warning(f"D-synced directory not found: {D_SYNCED_DIR}")
            return

        # Process all items in directory
        for item in D_SYNCED_DIR.rglob('*'):
            if item.is_dir() and item.name != '__pycache__':
                # Skip if it's the main d-synced folder
                if item != D_SYNCED_DIR:
                    self._process_folder(item)
            elif item.is_file():
                # Skip hidden files and JSON metadata files
                if not item.name.startswith('.') and not item.name.endswith('.json'):
                    self._process_file(item)

    def watch(self, interval: int = 60):
        """Watch directory for changes"""
        logger.info(f"Starting watch with {interval}s interval")
        
        try:
            while True:
                self.scan_directory()
                logger.debug(f"Scan complete, waiting {interval}s...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Watch stopped by user")
        except Exception as e:
            logger.error(f"Error during watch: {e}", exc_info=True)


def main():
    """Main entry point"""
    logger.info("Starting d-sync upload service")
    
    # Create webhooks.txt if it doesn't exist
    if not Path('webhooks.txt').exists():
        with open('webhooks.txt', 'w') as f:
            f.write("# Add Discord webhook URLs here, one per line\n")
            f.write("# Example: https://discordapp.com/api/webhooks/...\n")
        logger.info("Created webhooks.txt - add your Discord webhook URLs")
    
    upload = D_SyncUpload()
    upload.watch()


if __name__ == '__main__':
    main()
