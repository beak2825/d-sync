# d-sync Quick Start

🚀 Get started with d-sync in 5 minutes!

## 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 2️⃣ Get Discord Webhooks

1. Go to your Discord server
2. Server Settings → Integrations → Webhooks
3. Create 5-10 Webhooks across different channels
4. Copy each webhook URL

## 3️⃣ Add Webhooks

Paste your webhook URLs into `webhooks.txt` (one per line):
```
https://discordapp.com/api/webhooks/ID1/TOKEN1
https://discordapp.com/api/webhooks/ID2/TOKEN2
https://discordapp.com/api/webhooks/ID3/TOKEN3
```

## 4️⃣ Add Files to Sync

Create folders and files in `d-synced/`:
```bash
mkdir d-synced/MyProject
echo "Important data" > d-synced/important.txt
```

## 5️⃣ Upload!

Start the upload service:
```bash
python d_sync_upload.py
```

✅ Files will be:
- Compressed automatically
- Encrypted with your secure key
- Split into 9.99MB chunks
- Uploaded to Discord
- Tracked in `files.json`

## 6️⃣ Download Later

Restore all files anytime:
```bash
python d_sync_download.py
```

---

## What Happens Automatically?

| Step | What d-sync Does |
|------|-------------------|
| **Add file** | Detects new files in `d-synced/` |
| **Compress** | Files > 100KB are compressed (zlib) |
| **Encrypt** | All files encrypted with Fernet |
| **Partition** | Large files split into 9.99MB chunks |
| **Upload** | Each chunk sent to random webhook |
| **Save Metadata** | CDN URLs stored in `files.json` |
| **Download** | Retrieve chunks from Discord CDN |
| **Verify** | Check SHA256 hash of each chunk |
| **Decrypt** | Restore original encryption |
| **Decompress** | Restore original compression |
| **Restore** | File back to original state |

---

## Key Features

✨ **Automatic** - Just add files, it handles the rest  
🔐 **Secure** - Encrypted before upload  
📦 **Smart** - Automatically compresses large files  
⚡ **Fast** - Uses Discord CDN for downloads  
💾 **Complete Metadata** - Tracks everything  
📝 **Logged** - All operations logged  
🔄 **Recoverable** - Download anytime  
🎲 **Distributed** - Random webhooks prevent tracing  

---

## File Locations

| File | Purpose |
|------|---------|
| `d-synced/` | Your files go here |
| `files.json` | Auto-generated file metadata |
| `folders.json` | Auto-generated folder metadata |
| `webhooks.txt` | Your Discord webhook URLs |
| `.encryption_key` | Your encryption key (KEEP SAFE!) |
| `logs/` | All operation logs |

---

## Important Notes

⚠️ **Backup your `.encryption_key`** - You need it to decrypt files!

📌 **Keep `files.json` safe** - It contains CDN URLs to your files

🔗 **Add multiple webhooks** - Better distribution and redundancy

💬 **Check logs if troubles** - `logs/d-sync.log` has all details

---

## Common Tasks

### Upload all files
```bash
python d_sync_upload.py
```

### Download all files
```bash
python d_sync_download.py
```

### Delete a file (mark as deleted)
```bash
# Just delete it from d-synced/
rm d-synced/myfile.txt
# File marked as deleted in files.json
# But kept on Discord for recovery
```

### Monitor uploads
```bash
# Watch logs in real-time
tail -f logs/d-sync.log
```

### Check uploaded files
```bash
# View files.json to see all uploaded files
cat files.json
```

---

## Troubleshooting

**Q: "No webhooks available"**
- Check `webhooks.txt` has valid URLs

**Q: File not uploading**
- Check logs: `logs/d-sync.log`
- Verify webhook URLs work
- Check internet connection

**Q: Can't decrypt files**
- You need the `.encryption_key` file
- Without it, files are irrecoverable

**Q: Hash mismatch during download**
- Try downloading again
- Check Discord CDN is accessible

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Add webhooks
3. ✅ Add files to `d-synced/`
4. ✅ Run `python d_sync_upload.py`
5. ✅ When done, run `python d_sync_download.py`

For more details, see:
- [README.md](README.md) - Full documentation
- [SETUP.md](SETUP.md) - Detailed setup
- [EXAMPLES.md](EXAMPLES.md) - Usage examples

---

**You're all set!** 🎉

d-sync will now automatically sync files to Discord whenever you add them to `d-synced/`.
