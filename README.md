# d-sync: Discord File Synchronization System

A Python-based file synchronization system that uses Discord webhooks as unlimited cloud storage. Automatically uploads files with compression and encryption, and can restore them anytime.

## Features

✨ **Automatic File Sync** - Monitor `d-synced` folder and automatically upload new files
🔐 **Encryption** - Files are encrypted with Fernet symmetric encryption before upload
📦 **Compression** - Files larger than 100KB are automatically compressed with zlib
🔗 **File Partitioning** - Large files are split into 9.99MB chunks for Discord
🎲 **Random Webhook Selection** - Each chunk is uploaded to a random webhook for security and load balancing
💾 **Complete Metadata** - Stores detailed information about files, folders, hashes, and CDN URLs
📝 **Logging** - All operations are logged to files for auditing
📂 **Folder Structure** - Automatically creates and tracks folder metadata
🔄 **Download & Restore** - Easily download and restore encrypted/compressed files

## Project Structure

```
d-sync/
├── d-synced/              # Main folder to sync (add your folders/files here)
├── logs/                  # Log files
│   ├── d-sync.log         # Main log
│   ├── upload.log         # Upload responses
│   └── download.log       # Download responses
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── config.py          # Configuration and constants
│   ├── logger.py          # Logging utilities
│   ├── encryption.py      # Encryption/decryption
│   ├── compression.py     # Compression/decompression
│   ├── hashing.py         # File hashing (SHA256)
│   └── webhook_handler.py # Discord webhook management
├── d_sync_upload.py       # Main upload script
├── d_sync_download.py     # Download/restore script
├── files.json             # File metadata (auto-generated)
├── folders.json           # Folder metadata (auto-generated)
├── webhooks.txt           # Discord webhook URLs (add your own)
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone or download this repository:
```bash
cd d-sync
```

2. Install required dependencies:
```bash
pip install requests cryptography
```

3. Create Discord webhooks:
   - Go to your Discord server
   - Server Settings → Integrations → Webhooks
   - Click "Create Webhook"
   - Give it a name (e.g., "d-sync-storage")
   - Copy the webhook URL
   - Create multiple webhooks for better distribution and redundancy

4. Add webhook URLs to `webhooks.txt`:
```
https://discordapp.com/api/webhooks/YOUR_ID_1/YOUR_TOKEN_1
https://discordapp.com/api/webhooks/YOUR_ID_2/YOUR_TOKEN_2
https://discordapp.com/api/webhooks/YOUR_ID_3/YOUR_TOKEN_3
```

## Usage

### Uploading Files

1. Add files/folders to the `d-synced` folder:
```
d-synced/
├── MyProject/
│   ├── document.pdf
│   └── image.png
└── backup.zip
```

2. Run the upload script:
```bash
python d_sync_upload.py
```

The script will:
- Monitor the `d-synced` folder
- Detect new files and folders
- Compress files (> 100KB)
- Encrypt all files
- Partition into 9.99MB chunks
- Upload to Discord via webhooks
- Save metadata to `files.json` and `folders.json`
- Log all responses to `logs/upload.log`

3. Keep the script running to automatically sync new files as they're added

The script checks every 60 seconds for new files. You can modify this interval by changing the `watch()` call parameter.

### Downloading Files

Once files are uploaded, use:

```bash
python d_sync_download.py
```

This script will:
- Read `files.json` for file metadata
- Download all chunks from Discord CDN
- Verify chunk hashes
- Decrypt encrypted files
- Decompress compressed files
- Restore files to their original locations in `d-synced`
- Log all operations to `logs/download.log`

### Understanding the JSON Files

#### files.json Structure
```json
{
  "last_updated": "2026-02-16T12:34:56",
  "files": {
    "MyProject/document.pdf": {
      "file_path": "MyProject/document.pdf",
      "file_hash": "abc123...",
      "file_size": 1048576,
      "date_created": "2026-02-16T10:00:00",
      "file_type": ".pdf",
      "compressed": true,
      "encrypted": true,
      "deleted": false,
      "chunks": [
        {
          "chunk_index": 0,
          "chunk_hash": "def456...",
          "webhook_url": "https://discordapp.com/api/webhooks/...",
          "cdn_url": "https://cdn.discordapp.com/..."
        },
        {
          "chunk_index": 1,
          "chunk_hash": "ghi789...",
          "webhook_url": "https://discordapp.com/api/webhooks/...",
          "cdn_url": "https://cdn.discordapp.com/..."
        }
      ]
    }
  }
}
```

#### folders.json Structure
```json
{
  "last_updated": "2026-02-16T12:34:56",
  "folders": {
    "MyProject": {
      "folder_path": "MyProject",
      "date_created": "2026-02-16T10:00:00",
      "file_count": 5,
      "folder_count": 2,
      "cdn_url": "https://cdn.discordapp.com/..."
    }
  }
}
```

## Marking Files as Deleted

To delete files without removing them from Discord (for recovery purposes):

1. Delete the file from the `d-synced` folder
2. The file will automatically be marked as `"deleted": true` in `files.json`
3. The download script will skip deleted files
4. Files remain on Discord for archival purposes

## Security Features

### Encryption
- **Method**: Fernet (AES-128 in CBC mode)
- **Key Storage**: `.encryption_key` file (created on first run)
- **Permissions**: Encryption key has restricted file permissions (0o600)
- **First Run**: Generate a unique key and store it securely

### Compression
- **Method**: zlib compression
- **Level**: 6 (balanced compression)
- **Applied To**: Files larger than 100KB
- **Ratio**: Typically 3-10x compression for text/logs

### File Verification
- **Hash Algorithm**: SHA256
- **File Hash**: Calculated before encryption
- **Chunk Hashes**: Calculated for each chunk
- **Verification**: Downloaded chunks are verified before reconstruction

## Metadata Fields

### File Metadata
- `file_path`: Relative path from d-synced
- `file_hash`: SHA256 hash of original file
- `file_size`: Size in bytes
- `date_created`: ISO 8601 timestamp
- `file_type`: File extension
- `compressed`: Boolean - was file compressed
- `encrypted`: Boolean - was file encrypted
- `deleted`: Boolean - marked for deletion
- `chunks`: Array of chunk information

### Chunk Information
- `chunk_index`: Sequential chunk number (0-based)
- `chunk_hash`: SHA256 hash of chunk
- `webhook_url`: Which webhook was used
- `cdn_url`: Discord CDN URL for direct access

## Logging

All operations are logged to multiple places:

1. **Console Output**: INFO level and above
2. **logs/d-sync.log**: DEBUG level and above (all operations)
3. **logs/upload.log**: Webhook response data (JSON format)
4. **logs/download.log**: Download status and messages

Example log entry:
```
2026-02-16 12:34:56 - __main__ - INFO - Successfully uploaded file: MyProject/document.pdf
```

## Advanced Configuration

Edit `utils/config.py` to customize:

```python
MAX_PARTITION_SIZE = 9.99 * 1024 * 1024  # 9.99 MB
COMPRESSION_LEVEL = 6  # 0-9 (0=off, 9=max)
CHUNK_SIZE = 1024 * 1024  # Read buffer size (1 MB)
ENCRYPTION_ENABLED = True  # Enable/disable encryption
COMPRESSION_ENABLED = True  # Enable/disable compression
```

## Webhook Best Practices

1. **Multiple Webhooks**: Use at least 5-10 webhooks spread across different channels
2. **Separate Channels**: Create channels specifically for d-sync storage
3. **Channel Retention**: Webhooks can survive channel renames but not deletions
4. **Backup Webhooks**: Update `webhooks.txt` periodically if channels are deleted
5. **Rate Limiting**: Discord has rate limits (50 files/second per webhook)

## Limitations & Considerations

- Discord has a 25MB max file size, but d-sync partitions files to 9.99MB
- Webhook files are not deleted automatically; manage Discord storage manually
- Each chunk needs a unique filename to prevent collisions
- First run will generate an encryption key - **never lose this key!**
- Random webhook selection helps distribute load and improve reliability

## Troubleshooting

### No Webhooks Available
- Check `webhooks.txt` exists and contains valid webhook URLs
- Ensure webhooks are line-separated with no extra spaces
- Test webhook URLs manually in a browser

### Hash Mismatch During Download
- Network error during download interrupted integrity
- Try downloading again
- Check Discord CDN is accessible

### File Already Tracked
- File was previously uploaded
- To re-upload, delete the entry from `files.json` and try again

### Encryption Key Lost
- You must have your `.encryption_key` file to decrypt files
- If lost, encrypted files cannot be decrypted
- Store backup copies of `.encryption_key` in a safe location

## Performance Tips

1. **Upload Speed**: Upload speed depends on internet and Discord servers
2. **Large Files**: Partition can take time; monitor logs
3. **Memory**: Entire files are loaded into memory before processing
4. **Cleanup**: Periodically clean up Discord channels to prevent accumulation

## License

Free to use and modify for personal use.

## Support

Check the logs in `logs/` folder for detailed error messages.

Common issues:
- Missing webhooks → Add to `webhooks.txt`
- Permission errors → Check folder permissions
- Network errors → Check internet connection
- Encryption errors → Ensure `.encryption_key` file exists

## Future Enhancements

- [ ] Streaming uploads for very large files
- [ ] Delta sync (only upload changes)
- [ ] Multi-threading for faster uploads
- [ ] Web dashboard for monitoring
- [ ] Selective encryption/compression
- [ ] S3 fallback support
- [ ] Progress bar for uploads/downloads
