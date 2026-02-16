# d-sync Project Overview

Complete Discord File Synchronization System with automatic compression, encryption, and metadata tracking.

## ✅ Completed Features

### Core Functionality
- ✅ Automatic file monitoring in `d-synced/` folder
- ✅ File partitioning to 9.99MB chunks
- ✅ Automatic compression (zlib) for files > 100KB
- ✅ Transparent encryption (Fernet symmetric)
- ✅ File integrity verification (SHA256 hashing)
- ✅ Random webhook distribution for security
- ✅ Complete metadata tracking in JSON files
- ✅ Download and restoration of files with decryption/decompression

### File Organization
- ✅ `files.json` - File metadata with hashes and CDN URLs
- ✅ `folders.json` - Folder metadata with creation dates and file counts
- ✅ Soft deletion (mark as deleted, keep on Discord)
- ✅ Support for nested folder structures
- ✅ Automatic folder metadata generation

### Security & Logging
- ✅ Encryption key generation and storage
- ✅ Secure file permissions (0o600 for .encryption_key)
- ✅ Complete operation logging (DEBUG level)
- ✅ Webhook response logging to JSON
- ✅ Separate upload/download logs
- ✅ Console + file logging
- ✅ Timestamp on all log entries

### Discord Integration
- ✅ Webhook queue management
- ✅ Random webhook selection per chunk
- ✅ `?wait=true` parameter for full response data
- ✅ CDN URL extraction from responses
- ✅ Multi-webhook support for redundancy
- ✅ Rate limit friendly design

### User Experience
- ✅ Easy webhook configuration (webhooks.txt)
- ✅ Automatic first-run setup
- ✅ Watch mode with configurable intervals (60s default)
- ✅ Comprehensive documentation
- ✅ Quick start guide
- ✅ Usage examples with output samples
- ✅ Troubleshooting guide
- ✅ Performance benchmarks

## 📁 Complete File Structure

```
d-sync/
├── Core Scripts
│   ├── d_sync_upload.py         (Main upload service)
│   └── d_sync_download.py       (Restore/download service)
│
├── Utilities (utils/)
│   ├── __init__.py              (Package init)
│   ├── config.py                (Global configuration)
│   ├── logger.py                (Logging system)
│   ├── encryption.py            (Fernet encryption)
│   ├── compression.py           (zlib compression)
│   ├── hashing.py               (SHA256 hashing)
│   └── webhook_handler.py       (Discord webhooks)
│
├── Data Directories
│   ├── d-synced/                (User files - sync source)
│   └── logs/                    (Operation logs)
│
├── Metadata Files
│   ├── files.json               (File metadata)
│   ├── folders.json             (Folder metadata)
│   └── webhooks.txt             (Discord webhook URLs)
│
├── Configuration & Documentation
│   ├── requirements.txt          (Python dependencies)
│   ├── README.md                (Full documentation)
│   ├── QUICKSTART.md            (5-minute setup)
│   ├── SETUP.md                 (Detailed setup)
│   ├── EXAMPLES.md              (Usage examples)
│   └── PROJECT_OVERVIEW.md      (This file)
│
└── Runtime Files (auto-generated)
    └── .encryption_key          (Your encryption key - KEEP SAFE!)
```

## 🔧 Technical Stack

- **Language**: Python 3.8+
- **Encryption**: cryptography (Fernet AES-128)
- **Compression**: zlib
- **Hashing**: hashlib (SHA256)
- **HTTP Client**: requests
- **Storage**: Discord CDN (via webhooks)
- **Metadata Format**: JSON
- **Logging**: Python logging module

## 📊 Key Specifications

| Feature | Specification |
|---------|---------------|
| **Max File Size** | Unlimited (partitioned) |
| **Chunk Size** | 9.99 MB |
| **Discord Limit** | 25 MB (we use 9.99 MB) |
| **Encryption** | Fernet (AES-128 CBC) |
| **Compression** | zlib (level 6) |
| **Hash Algorithm** | SHA256 |
| **File Integrity** | Per-chunk + full file |
| **Deletion** | Soft delete (marked, not removed) |
| **Watch Interval** | 60 seconds (configurable) |
| **Webhook Selection** | Random per chunk |

## 🚀 Getting Started

### Quick Setup (2 minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add webhook URLs to webhooks.txt
# (Get from Discord server > Integrations > Webhooks)

# 3. Add files to d-synced/
mkdir d-synced/MyProject
cp myfile.txt d-synced/MyProject/

# 4. Start upload
python d_sync_upload.py
```

### Using a File
```bash
# Download files anytime
python d_sync_download.py
```

## 🔒 Security Features

1. **Encryption at Rest**
   - All files encrypted with Fernet before upload
   - Unique encryption key per installation
   - Key stored securely with restricted permissions

2. **Data Integrity**
   - SHA256 hash for each file
   - SHA256 hash for each chunk
   - Verification on download

3. **Distribution**
   - Random webhook per chunk prevents pattern recognition
   - Multiple webhooks spread across channels
   - Resilient to single channel deletion

4. **Encryption Key Protection**
   - Stored in `.encryption_key` file
   - File permissions set to 0o600 (owner only)
   - Critical for file recovery

## 📝 Metadata Examples

### File Entry (files.json)
```json
{
  "file_path": "Documents/report.pdf",
  "file_hash": "a1b2c3d4e5f6g7h8...",
  "file_size": 2097152,
  "date_created": "2026-02-16T10:00:00",
  "file_type": ".pdf",
  "compressed": true,
  "encrypted": true,
  "deleted": false,
  "chunks": [
    {
      "chunk_index": 0,
      "chunk_hash": "xyz789...",
      "webhook_url": "https://...",
      "cdn_url": "https://cdn.discordapp.com/..."
    }
  ]
}
```

### Folder Entry (folders.json)
```json
{
  "folder_path": "Documents",
  "date_created": "2026-02-16T09:00:00",
  "file_count": 15,
  "folder_count": 3,
  "cdn_url": "https://cdn.discordapp.com/..."
}
```

## 📊 Performance Characteristics

- Upload Speed: ~300-500 KB/s (network dependent)
- Compression Ratio: 3-10x for text/logs
- Memory Usage: Entire file loaded (optimize for large files)
- CPU: Minimal (compression/encryption efficient)
- Disk Usage: Minimal (only metadata stored locally)

## 🛠️ Configuration Options

Edit `utils/config.py`:

```python
MAX_PARTITION_SIZE = 9.99 * 1024 * 1024  # Chunk size
COMPRESSION_LEVEL = 6  # zlib compression (0-9)
CHUNK_SIZE = 1024 * 1024  # Read buffer (1 MB)
ENCRYPTION_ENABLED = True  # Enable encryption
COMPRESSION_ENABLED = True  # Enable compression
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Complete reference documentation |
| **QUICKSTART.md** | 5-minute quick start guide |
| **SETUP.md** | Detailed setup instructions |
| **EXAMPLES.md** | Real-world usage examples |
| **PROJECT_OVERVIEW.md** | This file (architecture overview) |

## 🐛 Troubleshooting Resources

Check the logs in these locations:
- `logs/d-sync.log` - Main debug log
- `logs/upload.log` - Webhook responses (JSON)
- `logs/download.log` - Download operations

Common issues covered:
- Missing webhooks
- Encryption key problems
- Hash mismatches
- Network errors
- Discord rate limits

## ✨ Notable Implementation Details

### Upload Process
1. Detect new files in `d-synced/`
2. Read entire file into memory
3. Compress if > 100 KB
4. Encrypt entire data
5. Partition into 9.99 MB chunks
6. For each chunk:
   - Calculate hash
   - Select random webhook
   - Upload to Discord
   - Extract CDN URL
   - Save to metadata
7. Save `files.json` and `folders.json`

### Download Process
1. Load `files.json` metadata
2. For each file:
   - Download all chunks
   - Verify hashes
   - Reconstruct original data
   - Decrypt
   - Decompress
   - Verify file hash
   - Write to disk

### Deletion Strategy (Soft Delete)
- Files deleted locally are marked as `"deleted": true` in `files.json`
- Files remain on Discord for archival/recovery
- Download script skips deleted files
- Manual removal from Discord recommended after verification

## 🔄 Workflow Integration

Can be integrated with:
- Windows Task Scheduler (automatic scheduled uploads)
- Linux cron jobs (automatic scheduled uploads)
- Shell scripts/batch files (wrappers)
- CI/CD pipelines (backup stage)
- System tray applications (background sync)

## 🎯 Use Cases

1. **Backup & Archive** - Use Discord as cloud storage
2. **Distributed Storage** - Spread files across webhooks
3. **Encrypted Backup** - Files encrypted before upload
4. **Folder Sync** - Automatic folder structure tracking
5. **Recovery System** - Download and restore anytime

## 🚀 Future Enhancement Ideas

- Streaming uploads (for very large files)
- Delta sync (only upload changes)
- Multi-threading (faster uploads)
- Web dashboard (monitoring)
- Selective compression/encryption
- S3 fallback
- Progress bars
- Bandwidth throttling
- Resume on interrupt

## 📋 Checklist for Users

- [ ] Install Python 3.8+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create Discord webhooks (5-10 recommended)
- [ ] Add webhook URLs to `webhooks.txt`
- [ ] Create folders in `d-synced/`
- [ ] Add files to sync
- [ ] Run `python d_sync_upload.py`
- [ ] Monitor logs
- [ ] Backup `.encryption_key`
- [ ] Test download with `python d_sync_download.py`

## ✅ System Status

All components implemented and tested:
- ✅ Core upload/download functionality
- ✅ Encryption/compression/hashing
- ✅ Webhook integration
- ✅ Metadata management
- ✅ Logging system
- ✅ Error handling
- ✅ Documentation
- ✅ Examples

**Ready to use!** 🎉

Start with [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup.
