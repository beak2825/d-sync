# D-Sync Quick Reference

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your webhook URLs to webhooks.txt
# 3. You're ready to go!
```

## Running D-Sync

### 🌐 Web Interface (Recommended)

**Option A: Windows Batch File**
```
Double-click: open_dsync.bat
```

**Option B: Python Launcher**
```bash
python open_dsync.py
```

**Option C: Direct Flask Run**
```bash
python d_sync_web.py
```

📍 Access at: http://localhost:5000

### ⚙️ Background Upload Service

Keep running in a terminal to automatically upload new files:

```bash
python d_sync_upload.py
```

Monitor logs:
```bash
# Real-time log viewing
tail -f logs/d-sync.log

# View upload responses
cat logs/upload.log
```

### 📥 Batch Download

Download all files from Discord:

```bash
python d_sync_download.py
```

Monitor logs:
```bash
cat logs/download.log
```

## Workflow

### Simple 3-Step Workflow

```
1. Add files to d-synced/
        ↓
2. Files auto-upload via d_sync_upload.py
        ↓
3. Download anytime via web interface or d_sync_download.py
```

### Typical Daily Usage

```bash
# Terminal 1 - Start upload service
python d_sync_upload.py

# Terminal 2 - Start web interface (in another terminal)
python d_sync_web.py

# Or on Windows, double-click open_dsync.bat for web interface
```

Then:
- Drag files to `d-synced/` folder
- Access dashboard at http://localhost:5000
- Click Download to restore files

## File Organization

```
d-synced/                    ← Put your files here
├── Documents/               ← Create folders to organize
│   ├── report.pdf
│   └── notes.txt
├── Backups/
│   └── database.backup
└── ProjectA/
    ├── code.zip
    └── logs.txt
```

## Web Dashboard Features

### Upload
- Drag & drop interface
- Click "Select Files"
- Files automatically queued

### Browse
- Real-time file list
- Most recent first
- Shows size, date, encryption status
- Live updates every 2 seconds

### Download
- One-click downloads
- Automatic decryption/decompression
- CDN refresh on 404

### Delete
- Soft delete (marked deleted)
- Files kept on Discord
- Can be recovered

### Statistics
- Total files
- Storage used
- Files encrypted
- Files compressed

## Keyboard Shortcuts

While planned for future, currently use mouse/touch.

## Useful Commands

### View File Metadata
```bash
# See all uploaded files
cat files.json | more

# See all folders
cat folders.json
```

### Check Storage Usage
```bash
# Total size
python -c "
import json
with open('files.json') as f:
    data = json.load(f)
    total = sum(m['file_size'] for m in data['files'].values())
    print(f'Total: {total / 1024 / 1024:.2f} MB')
"
```

### Monitor Background Upload
```bash
# Watch upload progress
tail -f logs/d-sync.log | grep "Successfully uploaded"
```

### View Recent Downloads
```bash
# See last 10 downloads
tail -10 logs/download.log
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Dashboard won't open | Open `http://localhost:5000` manually in Chrome |
| Port 5000 in use | Edit `d_sync_web.py`, change to different port |
| Can't upload files | Check webhooks in `webhooks.txt` |
| Download fails (404) | File > 24 hours old, may need refresh |
| Missing webhooks | Get from Discord, paste in `webhooks.txt` |
| Lost .encryption_key | All files encrypted, unrecoverable without key |

## File Locations

| Path | Purpose |
|------|---------|
| `d-synced/` | Your file storage folder |
| `files.json` | File metadata |
| `folders.json` | Folder metadata |
| `webhooks.txt` | Discord webhook URLs |
| `.encryption_key` | Your encryption key (BACKUP!) |
| `logs/` | Operation logs |

## Security

✅ **What's Encrypted:**
- All files encrypted before upload
- SHA256 verification on chunks
- Encryption key stored locally

⚠️ **Important:**
- Backup `.encryption_key` file
- Never share webhook URLs
- Keep `files.json` safe

## Performance

Typical upload/download speeds:
- Small files (< 10 MB): 2-5 seconds
- Medium files (10-100 MB): 20-60 seconds  
- Large files (> 100 MB): 1-5 minutes

Depends on:
- Internet connection
- Number of webhooks
- Discord rate limits
- File size

## Limits

| Item | Limit | Notes |
|------|-------|-------|
| File Size | Unlimited | Auto-partitioned to 9.99 MB chunks |
| Chunk Size | 9.99 MB | Discord max is 25 MB |
| Total Storage | Depends on Discord | Use multiple servers if needed |
| Webhook Count | 10+ recommended | More = faster uploads |
| Upload Speed | 300-500 KB/s | Network dependent |

## Tips & Tricks

1. **Multiple Webhooks** → Add 10+ for best distribution
2. **Organize Folders** → Use folder structure in `d-synced/`
3. **Regular Backups** → Schedule uploads weekly
4. **Monitor Logs** → Check `logs/d-sync.log` regularly
5. **Test Downloads** → Periodically verify files restore correctly
6. **Backup Encryption Key** → Store `.encryption_key` in safe place

## Getting Help

1. Check logs:
   ```bash
   cat logs/d-sync.log
   cat logs/download.log
   ```

2. Read documentation:
   - `README.md` - Full reference
   - `WEB_INTERFACE.md` - Dashboard guide
   - `EXAMPLES.md` - Real-world examples
   - `PROJECT_OVERVIEW.md` - Architecture

3. Verify setup:
   - Check `webhooks.txt` has valid URLs
   - Check `files.json` exists
   - Check internet connection
   - Check Discord webhooks still exist

## Scripts Summary

| Script | Purpose | Runs |
|--------|---------|------|
| `d_sync_upload.py` | Auto-upload to Discord | Continuously |
| `d_sync_download.py` | Download files | On-demand |
| `d_sync_web.py` | Web dashboard | Continuously |
| `open_dsync.py` | Launch dashboard | One-time |
| `open_dsync.bat` | Launch dashboard (Windows) | One-time |

## Future Enhancements

Coming soon:
- [ ] Real-time progress bars
- [ ] Bulk download/zip
- [ ] File search
- [ ] Share links
- [ ] Mobile app
- [ ] Bandwidth throttling
- [ ] Delta sync

---

👉 **Start here:** Double-click `open_dsync.bat` or run `python open_dsync.py`

📖 **Learn more:** Read [README.md](README.md) and [WEB_INTERFACE.md](WEB_INTERFACE.md)
