"""Webhook management utilities for d-sync"""

import requests
from pathlib import Path
from typing import Optional, List, Dict
import random
import json
from .logger import Logger
from .config import WEBHOOKS_FILE, WEBHOOK_WAIT_PARAM

logger = Logger(__name__)


class WebhookManager:
    """Manages Discord webhook operations"""

    def __init__(self):
        self.webhooks = self._load_webhooks()

    def _load_webhooks(self) -> List[str]:
        """Load webhooks from webhooks.txt"""
        if not WEBHOOKS_FILE.exists():
            logger.warning(f"Webhooks file not found at {WEBHOOKS_FILE}")
            return []

        with open(WEBHOOKS_FILE, 'r') as f:
            webhooks = [line.strip() for line in f.readlines() if line.strip()]
        return webhooks

    def get_random_webhook(self) -> Optional[str]:
        """Get a random webhook URL"""
        if not self.webhooks:
            logger.error("No webhooks available")
            return None
        return random.choice(self.webhooks)

    def upload_file(self, webhook_url: str, file_path: Path, chunk_index: int = 0) -> Optional[Dict]:
        """Upload a file to Discord via webhook"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                # Add wait=true to get full response
                url = f"{webhook_url.rstrip('/')}{WEBHOOK_WAIT_PARAM}"
                response = requests.post(url, files=files, timeout=60)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None

    def upload_bytes(self, webhook_url: str, data: bytes, filename: str) -> Optional[Dict]:
        """Upload bytes to Discord via webhook"""
        try:
            files = {'file': (filename, data)}
            url = f"{webhook_url.rstrip('/')}{WEBHOOK_WAIT_PARAM}"
            response = requests.post(url, files=files, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload {filename}: {e}")
            return None

    def extract_cdn_url(self, response: Dict) -> Optional[str]:
        """Extract CDN URL from Discord webhook response"""
        try:
            if 'attachments' in response and len(response['attachments']) > 0:
                return response['attachments'][0]['url']
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract CDN URL from response: {e}")
        return None
