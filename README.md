# d-sync: Discord File Synchronization System

A Python-based file synchronization system that uses Discord webhooks as unlimited cloud storage. Automatically uploads files with compression and encryption, and can restore them anytime.

## Features

✨ **Automatic File Sync** - Monitor `d-synced` folder and automatically upload new files
🌐 **Web Dashboard** - Beautiful localhost web interface for managing files
🔐 **Encryption** - Files are encrypted with Fernet symmetric encryption before upload
📦 **Compression** - Files larger than 100KB are automatically compressed with zlib
🔗 **File Partitioning** - Large files are split into 9.99MB chunks for Discord
🎲 **Random Webhook Selection** - Each chunk is uploaded to a random webhook for security and load balancing
💾 **Complete Metadata** - Stores detailed information about files, folders, hashes, and CDN URLs
📝 **Logging** - All operations are logged to files for auditing
📂 **Folder Structure** - Automatically creates and tracks folder metadata
🔄 **Download & Restore** - Easily download and restore encrypted/compressed files

## 🌐 Web Interface

Access the d-sync dashboard at `http://localhost:5000` to:
- 📤 Upload files via drag-and-drop
- 📂 Browse all uploaded files with real-time updates
- 📥 Download and restore files
- 🗑️ Delete files (soft delete)
- 📊 View storage statistics and encryption status
- ⏰ See relative timestamps ("2 hours ago", "just now", etc.)

### Quick Start Web Interface

```bash
# Option 1: Windows batch file (double-click)
open_dsync.bat

# Option 2: Python script
python open_dsync.py

# Option 3: Direct run
python d_sync_web.py

# Then open: http://localhost:5000
```

For detailed web interface documentation, see [WEB_INTERFACE.md](WEB_INTERFACE.md)

## Project Structure

```
d-sync/
├── Core Scripts
│   ├── d_sync_upload.py       # Main upload service
│   ├── d_sync_download.py     # Download/restore service
│   └── d_sync_web.py          # Web interface server
│
├── Launchers
│   ├── open_dsync.bat         # Windows launcher (double-click)
│   └── open_dsync.py          # Python launcher
│
├── Utilities (utils/)
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── logger.py              # Logging utilities
│   ├── encryption.py          # Encryption/decryption
│   ├── compression.py         # Compression/decompression
│   ├── hashing.py             # File hashing (SHA256)
│   ├── webhook_handler.py     # Discord webhook management
│   └── webhook_refresh.py     # Webhook message refresh
│
├── Data Directories
│   ├── d-synced/              # Your files go here
│   └── logs/                  # Operation logs
│
├── Metadata Files
│   ├── files.json             # File metadata (auto-generated)
│   ├── folders.json           # Folder metadata (auto-generated)
│   └── webhooks.txt           # Discord webhook URLs
│
├── Documentation
│   ├── README.md              # This file
│   ├── QUICKSTART.md          # 5-minute setup
│   ├── SETUP.md               # Detailed setup
│   ├── EXAMPLES.md            # Usage examples
│   ├── WEB_INTERFACE.md       # Web dashboard guide
│   └── PROJECT_OVERVIEW.md    # Architecture overview
│
├── Configuration
│   └── requirements.txt       # Python dependencies
│
└── Runtime Files (auto-generated)
    └── .encryption_key       # Your encryption key
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Chrome/Chromium (for web interface)

### Setup

1. Clone or download this repository:
```bash
cd d-sync
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP library for Discord API
- `cryptography` - For Fernet encryption
- `flask` - For web interface

3. Create Discord webhooks:
   - Go to your Discord server
   - Server Settings → Integrations → Webhooks
   - Click "Create Webhook"
   - Give it a name (e.g., "d-sync-storage")
   - Copy the webhook URL
   - Create multiple webhooks (5-10 recommended) for better distribution and redundancy

4. Add webhook URLs to `webhooks.txt`:
```
https://discord.com/api/webhooks/YOUR_ID_1/YOUR_TOKEN_1
https://discord.com/api/webhooks/YOUR_ID_2/YOUR_TOKEN_2
https://discord.com/api/webhooks/YOUR_ID_3/YOUR_TOKEN_3
```

## Usage

### Method 1: Using Web Interface (Recommended for Most Users)

**Start the Dashboard:**
```bash
# Windows - Double-click the batch file
open_dsync.bat

# Or run the Python launcher
python open_dsync.py

# Or start Flask directly
python d_sync_web.py
```

This will open `http://localhost:5000` in Chrome automatically.

**Using the Web Dashboard:**
1. **Upload Files:** Drag & drop files into the upload area (or click "Select Files")
2. **Monitor Status:** Watch real-time upload progress and storage statistics  
3. **Browse Files:** See all uploaded files sorted by date (most recent first)
4. **Download Files:** Click "Download" button to restore any file
5. **Delete Files:** Click "Delete" to mark as deleted (kept on Discord for recovery)

**Benefits:**
- 🖱️ Easy drag-and-drop interface
- 📊 Real-time status monitoring
- 📁 Browse files with rich metadata
- ⏰ Relative timestamps ("2 hours ago")
- 🔄 Live file list updates every 2 seconds
- 📱 Beautiful, responsive design

### Method 2: Command-Line Upload (For Automation)

#### Upload Files

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

### Download & Restore Files

#### Method 1: Web Interface (Easy)

1. Open the dashboard: `http://localhost:5000`
2. Browse files in the "Files" section
3. Click the **Download** button next to any file
4. Browser downloads the reconstructed file automatically
5. File is automatically decrypted and decompressed

#### Method 2: Command-Line (Batch)


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
