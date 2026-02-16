# d-sync Configuration Guide

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Discord Webhooks

Create or obtain Discord webhooks:
1. Go to your Discord server
2. Right-click a channel → Edit Channel
3. Go to Integrations → Webhooks
4. Click "Create Webhook"
5. Copy the webhook URL

Add webhooks to `webhooks.txt` (one per line):
```
https://discordapp.com/api/webhooks/ID1/TOKEN1
https://discordapp.com/api/webhooks/ID2/TOKEN2
```

### 3. First Run
The first run of `d_sync_upload.py` will:
- Create `.encryption_key` if it doesn't exist
- Create folder structure
- Initialize JSON metadata files
- Start watching `d-synced` folder

### 4. Usage

Upload files:
```bash
python d_sync_upload.py
```
Keep this running to sync new files automatically.

Download files:
```bash
python d_sync_download.py
```

### 5. Important Notes

⚠️ **Backup your `.encryption_key` file** - Without it, you cannot decrypt your files!

Files are partitioned to 9.99MB chunks (Discord limit: 25MB)

All operations are logged to `logs/` folder

## Customization

Edit `utils/config.py` to change:
- `MAX_PARTITION_SIZE`: File chunk size
- `COMPRESSION_LEVEL`: Compression (0-9)
- `ENCRYPTION_ENABLED`: Enable/disable encryption

## Security

- Files are encrypted before upload
- Webhooks are randomly selected for each chunk
- Chunk hashes are verified on download
- Encryption key is securely stored

## Troubleshooting

If something doesn't work:
1. Check `logs/d-sync.log` for errors
2. Verify webhooks in `webhooks.txt`
3. Ensure `.encryption_key` file exists
4. Check internet connection
