"""Configuration and constants for d-sync"""

import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
D_SYNCED_DIR = BASE_DIR / "d-synced"
LOGS_DIR = BASE_DIR / "logs"
UTILS_DIR = BASE_DIR / "utils"

# File size limits
MAX_PARTITION_SIZE = 9.99 * 1024 * 1024  # 9.99 MB in bytes
MIN_PARTITION_SIZE = 1024  # 1 KB minimum

# File configuration
WEBHOOKS_FILE = BASE_DIR / "webhooks.txt"
FOLDERS_JSON = BASE_DIR / "folders.json"
FILES_JSON = BASE_DIR / "files.json"

# Webhook options
WEBHOOK_WAIT_PARAM = "?wait=true"

# Logging
LOG_FILE = LOGS_DIR / "d-sync.log"
UPLOAD_LOG_FILE = LOGS_DIR / "upload.log"
DOWNLOAD_LOG_FILE = LOGS_DIR / "download.log"

# Encryption
ENCRYPTION_ENABLED = True
ENCRYPTION_KEY_FILE = BASE_DIR / ".encryption_key"

# Compression
COMPRESSION_ENABLED = True
COMPRESSION_LEVEL = 6  # 0-9, 6 is default

# Chunk size for reading files
CHUNK_SIZE = 1024 * 1024  # 1 MB

# Ensure directories exist
D_SYNCED_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
