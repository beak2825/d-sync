# d-sync Usage Examples

## Basic Workflow

### Step 1: Initial Setup

```bash
# Clone/navigate to d-sync directory
cd d-sync

# Install dependencies
pip install -r requirements.txt

# Add webhook URLs to webhooks.txt
# (Use your own Discord webhook URLs)
```

### Step 2: Upload Files

```bash
# Create some test files in d-synced folder
mkdir d-synced/Documents
echo "Hello World" > d-synced/Documents/test.txt
echo "Secret data" > d-synced/backup.dat

# Start upload service
python d_sync_upload.py
```

Output:
```
2026-02-16 12:00:00 - __main__ - INFO - Starting d-sync upload service
2026-02-16 12:00:00 - __main__ - INFO - Scanning directory for changes...
2026-02-16 12:00:01 - __main__ - INFO - Processing folder: d-synced\Documents
2026-02-16 12:00:01 - __main__ - INFO - Uploaded folder metadata: Documents
2026-02-16 12:00:02 - __main__ - INFO - Processing file: d-synced\Documents\test.txt
2026-02-16 12:00:03 - __main__ - INFO - Compressed file: d-synced\Documents\test.txt
2026-02-16 12:00:03 - __main__ - INFO - Encrypted file: d-synced\Documents\test.txt
2026-02-16 12:00:03 - __main__ - INFO - Uploaded chunk 0: abc123_chunk_0.bin
2026-02-16 12:00:04 - __main__ - INFO - Successfully uploaded file: Documents/test.txt
```

### Step 3: Monitor Logs

Check upload progress:
```bash
# View main log (follows along)
tail -f logs/d-sync.log

# View upload responses JSON
cat logs/upload.log
```

### Step 4: Check Metadata

After upload, `files.json` will contain:
```json
{
  "last_updated": "2026-02-16T12:00:04",
  "files": {
    "Documents/test.txt": {
      "file_path": "Documents/test.txt",
      "file_hash": "abcd1234...",
      "file_size": 11,
      "date_created": "2026-02-16T12:00:00",
      "file_type": ".txt",
      "compressed": true,
      "encrypted": true,
      "deleted": false,
      "chunks": [
        {
          "chunk_index": 0,
          "chunk_hash": "efgh5678...",
          "webhook_url": "https://discordapp.com/api/webhooks/...",
          "cdn_url": "https://cdn.discordapp.com/attachments/..."
        }
      ]
    }
  }
}
```

### Step 5: Download Files

After files are uploaded, you can restore them:

```bash
# Download all files
python d_sync_download.py
```

Output:
```
2026-02-16 13:00:00 - __main__ - INFO - Starting d-sync download service
2026-02-16 13:00:00 - __main__ - INFO - Loaded metadata for 2 files
2026-02-16 13:00:00 - __main__ - INFO - Available files (2):
2026-02-16 13:00:00 - __main__ - INFO -   1. Documents/test.txt
2026-02-16 13:00:00 - __main__ - INFO -   2. backup.dat
2026-02-16 13:00:00 - __main__ - INFO - Starting download of all files
2026-02-16 13:00:01 - __main__ - INFO - Downloading file: Documents/test.txt
2026-02-16 13:00:02 - __main__ - INFO - Downloaded and verified chunk 0
2026-02-16 13:00:02 - __main__ - INFO - Decrypted file: Documents/test.txt
2026-02-16 13:00:02 - __main__ - INFO - Decompressed file: Documents/test.txt
2026-02-16 13:00:02 - __main__ - INFO - Successfully downloaded and reconstructed: Documents/test.txt
2026-02-16 13:00:05 - __main__ - INFO - Downloaded 2/2 files successfully downloaded
```

---

## Advanced Scenarios

### Scenario 1: Large File Upload

```bash
# Create a large file (100MB)
dd if=/dev/zero of=d-synced/largefile.bin bs=1M count=100

# Run upload - will partition into ~11 chunks
python d_sync_upload.py
```

The file will be:
1. Compressed (zlib)
2. Encrypted (Fernet)
3. Partitioned into chunks of 9.99MB each
4. Uploaded to random webhooks
5. All chunk CDN URLs stored in `files.json`

### Scenario 2: Delete a File Safely

```bash
# Remove file locally
rm d-synced/Documents/test.txt

# File will be marked as deleted in files.json
# Download script will skip deleted files
# BUT the file remains on Discord (for recovery)
```

Check `files.json`:
```json
{
  "deleted": true  // File marked for deletion
}
```

### Scenario 3: Multiple Folders with Many Files

```bash
# Create nested structure
mkdir -p d-synced/Projects/ProjectA/src
mkdir -p d-synced/Projects/ProjectA/docs
mkdir -p d-synced/Projects/ProjectB
mkdir -p d-synced/Backups

# Add files
touch d-synced/Projects/ProjectA/src/main.py
touch d-synced/Projects/ProjectA/src/utils.py
echo "Documentation" > d-synced/Projects/ProjectA/docs/README.md

# Upload (automatic recursive scan)
python d_sync_upload.py
```

Folder structure created:
```json
{
  "folders": {
    "Projects": { ... },
    "Projects/ProjectA": { ... },
    "Projects/ProjectA/src": { ... },
    "Projects/ProjectB": { ... },
    "Backups": { ... }
  }
}
```

---

## Integration Examples

### Shell Script Wrapper (Windows)

Create `sync.bat`:
```batch
@echo off
python d_sync_upload.py
pause
```

Then run with: `sync.bat`

### Scheduled Uploads (Windows Task Scheduler)

1. Create task to run `d_sync_upload.py` periodically
2. Set environment to keep running
3. Redirect output to logging file

### Linux Bash Wrapper

Create `sync.sh`:
```bash
#!/bin/bash
cd /path/to/d-sync
python3 d_sync_upload.py
```

Make executable:
```bash
chmod +x sync.sh
./sync.sh
```

---

## File Structure After Operations

```
d-sync/
├── d-synced/
│   ├── Documents/
│   │   └── test.txt              (uploaded, encrypted, compressed)
│   ├── backup.dat                (uploaded, encrypted, compressed)
│   └── largefile.bin             (uploaded in ~11 chunks)
├── logs/
│   ├── d-sync.log               (100+ KB of detailed logs)
│   ├── upload.log               (JSON responses from Discord)
│   └── download.log             (Download operation logs)
├── files.json                   (metadata for all files)
├── folders.json                 (metadata for all folders)
├── webhooks.txt                 (your webhook URLs)
├── .encryption_key              (encryption key - KEEP SAFE!)
└── ...
```

---

## Monitoring and Maintenance

### Check Upload Progress

```bash
# Real-time log watching
tail -f logs/d-sync.log

# Check last uploaded file
grep "Successfully uploaded" logs/d-sync.log | tail -1
```

### Verify File Integrity

```bash
# Check if all chunks downloaded successfully
python -c "
import json
with open('files.json') as f:
    data = json.load(f)
    for file_path, meta in data['files'].items():
        print(f'{file_path}: {len(meta[\"chunks\"])} chunks')
"
```

### Storage Statistics

```bash
# Calculate total uploaded size
python -c "
import json
with open('files.json') as f:
    data = json.load(f)
    total = sum(m['file_size'] for m in data['files'].values())
    print(f'Total size: {total / 1024 / 1024:.2f} MB')
"
```

---

## Troubleshooting Examples

### Issue: "No webhooks available"

**Problem**: Webhooks file missing or empty

**Solution**:
```bash
# Check webhooks.txt exists
cat webhooks.txt

# If empty, add webhook URLs
echo "https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN" >> webhooks.txt
```

### Issue: "Chunk hash mismatch"

**Problem**: Downloaded chunk was corrupted or truncated

**Solution**:
```bash
# Re-run download (will retry)
python d_sync_download.py

# Check Discord CDN is accessible
# Try downloading chunk URL directly in browser
```

### Issue: Files already tracked but want to re-upload

**Problem**: File was already uploaded and is in `files.json`

**Solution**:
```bash
# Edit files.json and remove the entry
# OR delete the file and re-add it
rm d-synced/myfile.txt
# Then add it back and run upload again
```

---

## Performance Benchmarks

Typical speeds (depends on internet and webhook count):

| File Size | Time | Speed |
|-----------|------|-------|
| 1 MB | 2-3s | ~350 KB/s |
| 10 MB | 20-30s | ~400 KB/s |
| 100 MB | 3-5 min | ~300-500 KB/s |
| 1 GB | 30-60 min | ~300-500 KB/s |

Note: Speed varies based on Discord rate limits, network, and webhook count.

---

## Security Checklist

- [ ] Backup `.encryption_key` file to safe location
- [ ] Use multiple webhooks (spread across channels)
- [ ] Don't share webhook URLs publicly
- [ ] Regularly backup `files.json` and `folders.json`
- [ ] Monitor logs for suspicious activity
- [ ] Update Python and dependencies periodically
- [ ] Test restore process periodically
