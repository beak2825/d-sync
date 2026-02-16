# D-Sync Web Interface Guide

The d-sync web interface provides an easy-to-use dashboard for managing your Discord-backed file storage.

## Overview

Access the web dashboard at `http://localhost:5000` to:
- 📤 Upload files (drag & drop or click)
- 📂 Browse all uploaded files
- 📥 Download and restore files
- 🗑️ Delete files (soft delete)
- 📊 View storage statistics
- ⏰ See relative timestamps (e.g., "2 hours ago")
- ✅ Monitor current upload status

## Getting Started

### Method 1: Using Batch File (Windows)
Simply double-click `open_dsync.bat`:
```
open_dsync.bat
```

### Method 2: Using Python Script
```bash
python open_dsync.py
```

### Method 3: Using Flask Directly
```bash
python d_sync_web.py
```

The dashboard will automatically open in Chrome.

## Features

### 📤 Upload Section

**Upload Files:**
1. Drag and drop files into the upload area, OR
2. Click "Select Files" button
3. Select one or more files
4. Files are saved to `d-synced/` folder
5. The background upload script picks them up and syncs to Discord

**Important Notes:**
- ❌ `.crdownload` files (incomplete downloads) are rejected
- ✅ Unlimited file size (partitioned to 9.99MB chunks)
- ✅ Automatic compression for files > 100KB
- ✅ Automatic encryption (transparent to you)
- 🎯 Multiple webhooks ensure redundancy

### 📂 File Browser

**File Listing Features:**
- ⏰ Files sorted by date (most recent first)
- 📊 Shows relative time ("just now", "2 hours ago", etc.)
- 💾 Displays file size
- 📦 Shows number of chunks
- 🔐 Badge for encrypted files
- 📦 Badge for compressed files

**Actions:**
- 📥 Download button - Reconstructs file from Discord
- 🗑️ Delete button - Marks file as deleted (kept on Discord)

### ⚙️ Status Section

Real-time information:
- 📤 Current upload status
- 📊 Total files count
- 💾 Total storage used
- 📝 Deleted files count

### 📈 Statistics

Footer statistics show:
- 📁 Total Files - Count of all files
- 💾 Storage Used - Total size of stored files
- 🔐 Encrypted - Count of encrypted files
- 📦 Compressed - Count of compressed files

## Upload Process Flow

```
You drag/drop file
         ↓
File saved to d-synced/
         ↓
d_sync_upload.py detects it (runs automatically)
         ↓
File compressed (if > 100KB)
         ↓
File encrypted
         ↓
File partitioned to 9.99MB chunks
         ↓
Each chunk uploaded to random webhook
         ↓
CDN URLs stored in files.json
         ↓
Dashboard updated with new file
```

## Download Process Flow

```
Click Download button
         ↓
Script downloads all chunks from Discord CDN
         ↓
Chunks verified (SHA256 hash check)
         ↓
File decrypted
         ↓
File decompressed
         ↓
Original file reconstructed
         ↓
Browser downloads file
```

## File Deletion

**Soft Delete:**
- Clicking "Delete" marks the file as deleted in `files.json`
- File remains on Discord for archival/recovery
- Download script skips deleted files
- Dashboard shows deleted files with strikethrough text

**To Permanently Remove from Discord:**
- Manually delete messages from Discord webhook channels
- Or clean up Discord storage periodically

## Special Cases

### Files Older Than 24 Hours

If a file hasn't been downloaded in 24+ hours:
- Discord CDN links may expire
- Web server attempts automatic refresh via webhook
- If refresh fails, download will be unavailable
- Solution: Re-upload the file or manually refresh

### .crdownload Files

Incomplete downloads (Chrome temp files):
- ❌ Cannot be uploaded via web interface
- ✅ Configuration prevents accidental uploads
- 💡 Let downloads complete before uploading

### Large Files

For files > 100MB:
- Split into multiple chunks
- Each chunk uploaded separately
- Uses random webhooks for distribution
- Download reassembles automatically

## API Endpoints

The web server provides JSON APIs:

### GET /api/files
Returns all files from `files.json`:
```json
{
  "last_updated": "2026-02-16T12:00:00",
  "files": {
    "filename.ext": {
      "file_path": "filename.ext",
      "file_hash": "sha256...",
      "file_size": 1024,
      "date_created": "ISO timestamp",
      "file_type": ".ext",
      "compressed": true,
      "encrypted": true,
      "deleted": false,
      "chunks": [...]
    }
  }
}
```

### POST /api/upload
Upload a file (form-data):
- `file`: The file to upload
- Returns: `{"success": true, "message": "..."}`

### GET /api/upload-status
Current upload status:
```json
{
  "is_uploading": false,
  "current_file": null,
  "progress": 0
}
```

### POST /api/delete/{filename}
Mark file as deleted:
- Returns: `{"success": true}`

### GET /download/{filename}
Download and reconstruct file from Discord

## Troubleshooting

### Dashboard Won't Open

**Problem:** Chrome doesn't open automatically

**Solution:**
1. Open Chrome manually
2. Go to `http://localhost:5000`
3. Check if server is running in terminal

### Can't Upload Files

**Problem:** Upload fails or times out

**Solution:**
1. Check file isn't in use
2. Verify webhooks are valid: check `webhooks.txt`
3. Check internet connection
4. Check logs: `logs/d-sync.log`

### File Won't Download

**Problem:** Download fails with 404 or error

**Solutions:**
1. File may be expired (> 24 hours) - refresh webhook
2. Discord webhook channel may be deleted
3. Add more webhooks to `webhooks.txt`
4. Check logs: `logs/download.log`

### Server Already Running

**Problem:** Port 5000 already in use

**Solution:** Change port in `d_sync_web.py`:
```python
start_server(port=5001)  # Use different port
```

Then access at: `http://localhost:5001`

## Configuration

Edit `d_sync_web.py` to customize:

```python
# Port (default: 5000)
start_server(port=5000)

# Auto-open browser (default: True)
start_server(open_browser=True)

# Max upload size (in bytes)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
```

## Advanced Features

### Real-time Updates
- Dashboard refreshes every 2 seconds
- Automatic status monitoring
- Live file list updates

### Relative Time Display
- "just now" - less than 1 minute
- "5 minutes ago"
- "2 hours ago"
- "3 days ago"
- "2 weeks ago"

### Progress Tracking
- Shows current file being processed
- Visual progress indicator
- Status messages

## Performance Notes

- Dashboard handles 1000+ files smoothly
- Real-time updates every 2 seconds
- Download speeds: 300-500 KB/s typical
- Upload speeds depend on webhook count

## Security

- 🔐 All files encrypted before leaving your computer
- 🎲 Random webhook distribution prevents pattern analysis
- ✅ SHA256 hash verification (file + chunks)
- 🔑 Encryption key stored securely locally
- 📝 All operations logged

## Tips & Tricks

1. **Multiple Webhooks:** Add 5-10 webhooks across different channels for better distribution
2. **Organize Files:** Use folders in `d-synced/` to organize your backups
3. **Regular Backups:** Schedule regular automated uploads
4. **Monitor Logs:** Check `logs/` for any issues
5. **Test Downloads:** Periodically test downloading files to ensure they work

## Keyboard Shortcuts

Coming in future version - currently requires mouse/touch.

## Browser Support

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Any modern browser supporting ES6

## Bandwidth Usage

Typical speeds and data:
- Upload: 300-500 KB/s
- Download: 300-500 KB/s
- Metadata: < 1KB per file
- Daily logs: 100-500 KB

## Integration

The web interface works alongside:
- `d_sync_upload.py` - Automatic background uploads
- `d_sync_download.py` - Command-line downloads
- Scheduled tasks/cron jobs

## Support

For issues or questions:
1. Check `logs/d-sync.log`
2. Check `logs/download.log`
3. Verify `webhooks.txt` has valid URLs
4. Verify `files.json` has metadata
5. Check Docker/network configuration if using remote access

## Future Enhancements

Planned features:
- [ ] Real-time file sync indicator
- [ ] Bulk download with zip
- [ ] Progress bar during uploads
- [ ] File preview (images, PDFs)
- [ ] Search functionality
- [ ] Folder view
- [ ] Share links
- [ ] Mobile responsive improvements
