"""
D-Sync Web Server
Serves a localhost interface for uploading and downloading files
"""

import os
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
import webbrowser
import time
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    Logger, D_SYNCED_DIR, FILES_JSON, WEBHOOKS_FILE, BASE_DIR,
    CompressionManager, EncryptionManager, HashManager
)
from utils.webhook_refresh import WebhookMessageRefresh

try:
    from flask import Flask, request, jsonify, send_file, render_template_string
except ImportError:
    print("Flask not installed. Install with: pip install flask")
    sys.exit(1)

logger = Logger("d_sync_web")

app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max
app.config['UPLOAD_FOLDER'] = str(D_SYNCED_DIR)

# Track current upload status
upload_status = {
    'is_uploading': False,
    'current_file': None,
    'progress': 0
}


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>d-sync - Discord File Storage</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 .icon {
            font-size: 1.2em;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }
        
        .upload-area:hover {
            background: #f0f2ff;
            border-color: #764ba2;
        }
        
        .upload-area.dragover {
            background: #e8ebff;
            border-color: #764ba2;
            transform: scale(1.02);
        }
        
        .upload-area input[type="file"] {
            display: none;
        }
        
        .upload-area p {
            color: #666;
            margin-bottom: 10px;
            font-size: 1em;
        }
        
        .upload-area .big {
            font-size: 2em;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .status-box {
            background: #f0f2ff;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #667eea;
            font-weight: 500;
        }
        
        .status-box.uploading {
            background: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }
        
        .status-box.ready {
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        
        .files-list {
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #fafafa;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
            transition: background 0.3s ease;
        }
        
        .file-item:last-child {
            border-bottom: none;
        }
        
        .file-item:hover {
            background: white;
        }
        
        .file-item.deleted {
            opacity: 0.6;
            text-decoration: line-through;
        }
        
        .file-info {
            flex: 1;
        }
        
        .file-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .file-meta {
            font-size: 0.85em;
            color: #999;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .file-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .file-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-download {
            background: #28a745;
            padding: 8px 16px;
            font-size: 0.9em;
        }
        
        .btn-download:hover {
            background: #218838;
        }
        
        .btn-delete {
            background: #dc3545;
            padding: 8px 16px;
            font-size: 0.9em;
        }
        
        .btn-delete:hover {
            background: #c82333;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }
        
        .empty-state p {
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .badge-encrypted {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-compressed {
            background: #cce5ff;
            color: #004085;
        }
        
        .file-size {
            color: #666;
            font-size: 0.9em;
        }
        
        .relative-time {
            color: #667eea;
            font-weight: 500;
        }
        
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        
        .progress-container.active {
            display: block;
        }
        
        .progress-bar {
            width: 100%;
            height: 25px;
            background: #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
        }
        
        .footer-stats {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.95em;
            margin-top: 5px;
        }
        
        .no-files {
            color: #999;
            text-align: center;
            padding: 20px;
            font-style: italic;
        }
        
        /* Scrollbar styling */
        .files-list::-webkit-scrollbar {
            width: 8px;
        }
        
        .files-list::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 8px;
        }
        
        .files-list::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 8px;
        }
        
        .files-list::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>☁️ d-sync</h1>
            <p>Secure Cloud File Storage</p>
        </header>
        
        <div class="main-content">
            <!-- Upload Card -->
            <div class="card">
                <h2><span class="icon">📤</span> Upload Files</h2>
                <div class="upload-area" id="uploadArea">
                    <div class="big">📁</div>
                    <p><strong>Drag files here or click to select</strong></p>
                    <p style="font-size: 0.9em; color: #999;">Files will be queued and uploaded to remote storage automatically</p>
                    <input type="file" id="fileInput" multiple>
                    <button type="button" onclick="document.getElementById('fileInput').click()">Select Files</button>
                </div>
                
                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill">0%</div>
                    </div>
                    <div style="text-align: center; color: #666;">
                        Uploading: <span id="progressFile"></span>
                    </div>
                </div>
                
                <div class="status-box" id="statusBox">
                    ✅ Ready to upload
                </div>
            </div>
            
            <!-- Upload Status Card -->
            <div class="card">
                <h2><span class="icon">⚙️</span> Status</h2>
                <div style="padding: 20px 0;">
                    <div style="margin-bottom: 20px;">
                        <p style="color: #999; margin-bottom: 10px;">Current Upload Status</p>
                        <div id="uploadStatus" style="font-size: 2em; color: #667eea; font-weight: bold;">
                            Not uploading
                        </div>
                    </div>
                    
                    <div style="border-top: 1px solid #e0e0e0; padding-top: 20px;">
                        <p style="color: #999; margin-bottom: 10px;">System Statistics</p>
                        <div id="stats" style="color: #333; line-height: 1.8;">
                            <p>📊 Total Files: <strong id="totalFiles">0</strong></p>
                            <p>💾 Total Size: <strong id="totalSize">0 MB</strong></p>
                            <p>📝 Deleted Files: <strong id="deletedCount">0</strong></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Files List -->
        <div class="card">
            <h2><span class="icon">📂</span> Files (Most Recent First)</h2>
            <div class="files-list" id="filesList">
                <div class="no-files">Loading files...</div>
            </div>
        </div>
        
        <!-- Footer Stats -->
        <div class="footer-stats" style="margin-top: 40px;">
            <div class="stat">
                <div class="stat-value" id="statTotalFiles">0</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="statTotalSize">0</div>
                <div class="stat-label">Storage Used</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="statEncrypted">0</div>
                <div class="stat-label">Encrypted</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="statCompressed">0</div>
                <div class="stat-label">Compressed</div>
            </div>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const statusBox = document.getElementById('statusBox');
        const progressContainer = document.getElementById('progressContainer');
        const filesList = document.getElementById('filesList');
        
        // Handle drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
            fileInput.value = '';
        });
        
        function handleFiles(files) {
            Array.from(files).forEach(file => {
                // Skip .crdownload files
                if (file.name.endsWith('.crdownload')) {
                    alert(`Cannot upload ${file.name} - incomplete downloads not allowed`);
                    return;
                }
                
                uploadFile(file);
            });
        }
        
        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            // Show progress
            progressContainer.classList.add('active');
            document.getElementById('progressFile').textContent = file.name;
            statusBox.textContent = `📤 Uploading ${file.name}...`;
            statusBox.classList.add('uploading');
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusBox.classList.remove('uploading');
                    statusBox.classList.add('ready');
                    statusBox.textContent = `✅ ${file.name} uploaded successfully`;
                    progressContainer.classList.remove('active');
                    loadFiles();
                    setTimeout(() => {
                        statusBox.classList.remove('ready');
                        statusBox.textContent = '✅ Ready to upload';
                    }, 3000);
                } else {
                    statusBox.textContent = `❌ Error: ${data.error}`;
                    statusBox.classList.add('uploading');
                }
            })
            .catch(error => {
                statusBox.textContent = `❌ Upload failed: ${error}`;
                progressContainer.classList.remove('active');
            });
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
        
        function getRelativeTime(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const secondsAgo = Math.floor((now - date) / 1000);
            
            if (secondsAgo < 60) return 'just now';
            if (secondsAgo < 3600) return Math.floor(secondsAgo / 60) + ' minutes ago';
            if (secondsAgo < 86400) return Math.floor(secondsAgo / 3600) + ' hours ago';
            if (secondsAgo < 604800) return Math.floor(secondsAgo / 86400) + ' days ago';
            return Math.floor(secondsAgo / 604800) + ' weeks ago';
        }
        
        function downloadFile(filename) {
            window.location.href = `/download/${encodeURIComponent(filename)}`;
        }
        
        function deleteFile(filename) {
            if (confirm(`Delete ${filename}? (File will be marked as deleted but kept in remote storage)`)) {
                fetch(`/api/delete/${encodeURIComponent(filename)}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadFiles();
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
        
        function loadFiles() {
            fetch('/api/files')
                .then(response => response.json())
                .then(data => {
                    const files = data.files || {};
                    const fileArray = Object.entries(files)
                        .map(([path, meta]) => ({path, ...meta}))
                        .sort((a, b) => new Date(b.date_created) - new Date(a.date_created));
                    
                    // Update stats
                    updateStats(fileArray);
                    
                    if (fileArray.length === 0) {
                        filesList.innerHTML = '<div class="no-files">No files uploaded yet. Upload some files above!</div>';
                        return;
                    }
                    
                    filesList.innerHTML = fileArray.map(file => `
                        <div class="file-item ${file.deleted ? 'deleted' : ''}">
                            <div class="file-info">
                                <div class="file-name">
                                    📄 ${file.file_path}
                                    ${file.encrypted ? '<span class="badge badge-encrypted">🔐 Encrypted</span>' : ''}
                                    ${file.compressed ? '<span class="badge badge-compressed">📦 Compressed</span>' : ''}
                                </div>
                                <div class="file-meta">
                                    <span>💾 ${formatFileSize(file.file_size || 0)}</span>
                                    <span class="relative-time">⏰ ${getRelativeTime(file.date_created)}</span>
                                    <span>📦 ${file.chunk_count || 0} chunk${(file.chunk_count || 0) !== 1 ? 's' : ''}</span>
                                </div>
                            </div>
                            <div class="file-actions">
                                ${!file.deleted ? `<button class="btn-download" onclick="downloadFile('${file.file_path.replace(/'/g, "\\'")}')">Download</button>` : ''}
                                ${!file.deleted ? `<button class="btn-delete" onclick="deleteFile('${file.file_path.replace(/'/g, "\\'")}')">Delete</button>` : '<span style="color: #999;">Deleted</span>'}
                            </div>
                        </div>
                    `).join('');
                })
                .catch(error => {
                    console.error('Error loading files:', error);
                    filesList.innerHTML = '<div class="no-files">Error loading files</div>';
                });
        }
        
        function updateStats(files) {
            const totalFiles = files.length;
            const activeFiles = files.filter(f => !f.deleted);
            const totalSize = activeFiles.reduce((sum, f) => sum + (f.file_size || 0), 0);
            const encrypted = activeFiles.filter(f => f.encrypted).length;
            const compressed = activeFiles.filter(f => f.compressed).length;
            const deleted = files.filter(f => f.deleted).length;
            
            document.getElementById('statTotalFiles').textContent = totalFiles;
            document.getElementById('statTotalSize').textContent = formatFileSize(totalSize);
            document.getElementById('statEncrypted').textContent = encrypted;
            document.getElementById('statCompressed').textContent = compressed;
            
            document.getElementById('totalFiles').textContent = totalFiles;
            document.getElementById('totalSize').textContent = (totalSize / 1024 / 1024).toFixed(2);
            document.getElementById('deletedCount').textContent = deleted;
        }
        
        function checkUploadStatus() {
            fetch('/api/upload-status')
                .then(response => response.json())
                .then(data => {
                    const statusEl = document.getElementById('uploadStatus');
                    if (data.is_uploading) {
                        statusEl.textContent = `📤 ${data.current_file} (${data.progress}%)`;
                    } else {
                        statusEl.textContent = '✅ Ready';
                    }
                })
                .catch(error => console.error('Error checking status:', error));
        }
        
        // Load files on startup
        loadFiles();
        checkUploadStatus();
        
        // Refresh every 2 seconds
        setInterval(() => {
            checkUploadStatus();
            loadFiles();
        }, 2000);
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/files', methods=['GET'])
def get_files():
    """Get all files from files.json but sanitize sensitive fields before returning to client."""
    try:
        if not FILES_JSON.exists():
            return jsonify({'files': {}})

        with open(FILES_JSON, 'r') as f:
            data = json.load(f)

        sanitized = {}
        for key, meta in data.get('files', {}).items():
            sanitized[key] = {
                'file_path': meta.get('file_path', key),
                'file_size': meta.get('file_size', 0),
                'date_created': meta.get('date_created'),
                'file_type': meta.get('file_type'),
                'compressed': meta.get('compressed', False),
                'encrypted': meta.get('encrypted', False),
                'deleted': meta.get('deleted', False),
                'chunk_count': len(meta.get('chunks', []))
            }

        return jsonify({'last_updated': data.get('last_updated'), 'files': sanitized})
    except Exception as e:
        logger.error(f"Error reading files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload to d-synced folder"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No filename'}), 400
        
        # Reject .crdownload files
        if file.filename.endswith('.crdownload'):
            return jsonify({'success': False, 'error': 'Cannot upload incomplete downloads (.crdownload)'}), 400
        
        # Save file to d-synced folder
        upload_status['is_uploading'] = True
        upload_status['current_file'] = file.filename
        
        file_path = D_SYNCED_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(file_path))
        
        upload_status['is_uploading'] = False
        upload_status['current_file'] = None
        
        logger.info(f"File uploaded via web: {file.filename}")
        return jsonify({'success': True, 'message': 'File uploaded successfully'})
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        upload_status['is_uploading'] = False
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload-status', methods=['GET'])
def get_upload_status():
    """Get current upload status"""
    return jsonify(upload_status)


@app.route('/api/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Mark file as deleted in files.json"""
    try:
        if FILES_JSON.exists():
            with open(FILES_JSON, 'r') as f:
                data = json.load(f)
            
            if filename in data.get('files', {}):
                data['files'][filename]['deleted'] = True
                with open(FILES_JSON, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"File marked as deleted: {filename}")
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file and reconstruct it from Discord"""
    try:
        # Reject .crdownload files
        if filename.endswith('.crdownload'):
            return jsonify({'error': 'Cannot download incomplete files'}), 400
        
        if not FILES_JSON.exists():
            return jsonify({'error': 'No files metadata'}), 404
        
        with open(FILES_JSON, 'r') as f:
            data = json.load(f)
        
        if filename not in data.get('files', {}):
            return jsonify({'error': 'File not found'}), 404
        
        file_meta = data['files'][filename]
        
        # Check if file is deleted
        if file_meta.get('deleted'):
            return jsonify({'error': 'File has been deleted'}), 410
        
        # Download from Discord
        from d_sync_download import D_SyncDownload
        downloader = D_SyncDownload()
        
        # Download and reconstruct
        success = downloader.download_file(filename)
        if not success:
            return jsonify({'error': 'Failed to download file'}), 500
        
        # Send the reconstructed file. check known output locations (d-synced and d-synced2)
        candidates = [D_SYNCED_DIR / filename, BASE_DIR / 'd-synced2' / filename]
        for p in candidates:
            if p.exists():
                return send_file(str(p), as_attachment=True, download_name=filename)

        return jsonify({'error': 'File not found after download'}), 500
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


def start_server(port=5000, open_browser=True):
    """Start the Flask server"""
    logger.info(f"Starting d-sync web server on http://localhost:{port}")
    
    if open_browser:
        # Open in browser after a short delay
        def open_browser_delayed():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    app.run(host='localhost', port=port, debug=False, use_reloader=False)


def main():
    """Main entry point"""
    logger.info("Starting d-sync web interface")
    start_server(port=5000, open_browser=True)


if __name__ == '__main__':
    main()
