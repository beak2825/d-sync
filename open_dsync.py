#!/usr/bin/env python3
"""
D-Sync Web Interface Launcher
Opens the D-Sync dashboard in Chrome
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from d_sync_web import start_server

if __name__ == '__main__':
    print("🚀 Starting d-sync web interface...")
    print("📱 Opening dashboard in Chrome...")
    print("🌐 Access at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    start_server(port=5000, open_browser=True)
