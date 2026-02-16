"""Webhook message refresh utilities for d-sync"""

import requests
from datetime import datetime, timedelta
import json
from pathlib import Path
from .logger import Logger
from .config import FILES_JSON

logger = Logger(__name__)


class WebhookMessageRefresh:
    """Handles refreshing webhook message IDs when CDN links expire"""

    @staticmethod
    def parse_webhook_url(webhook_url: str) -> tuple:
        """Parse webhook URL to get webhook_id and webhook_token"""
        parts = webhook_url.strip('/').split('/')
        webhook_id = parts[-2]
        webhook_token = parts[-1]
        return webhook_id, webhook_token

    @staticmethod
    def get_webhook_messages(webhook_url: str, limit: int = 100) -> list:
        """Get recent messages from webhook channel"""
        try:
            webhook_id, webhook_token = WebhookMessageRefresh.parse_webhook_url(webhook_url)
            
            # Get channel ID from webhook
            webhook_info_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
            response = requests.get(webhook_info_url, timeout=10)
            response.raise_for_status()
            webhook_data = response.json()
            
            channel_id = webhook_data.get('channel_id')
            if not channel_id:
                logger.error("Could not get channel ID from webhook")
                return []

            # Get messages from channel
            messages_url = f"https://discord.com/api/channels/{channel_id}/messages?limit={limit}"
            
            # Note: This requires a bot token, not a webhook token
            # For now, we'll try with webhook token (may fail)
            response = requests.get(messages_url, timeout=10)
            
            if response.status_code == 401:
                logger.warning("Cannot access channel messages with webhook token")
                return []
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get webhook messages: {e}")
            return []

    @staticmethod
    def refresh_chunk_urls(file_metadata: dict, webhook_url: str) -> bool:
        """
        Refresh CDN URLs for chunks by getting webhook message data
        
        If a file is > 24 hours old, we try to refresh the message IDs
        by using the webhook GET endpoint to retrieve message data
        """
        try:
            webhook_id, webhook_token = WebhookMessageRefresh.parse_webhook_url(webhook_url)
            
            # Get webhook info (includes channel)
            webhook_info_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
            response = requests.get(webhook_info_url, timeout=10)
            response.raise_for_status()
            webhook_data = response.json()
            
            channel_id = webhook_data.get('channel_id')
            if not channel_id:
                logger.error("Could not get channel ID from webhook")
                return False

            # Find messages in channel that match our chunks
            messages_url = f"https://discord.com/api/channels/{channel_id}/messages?limit=100"
            
            # This requires a bot token - for now we can't do this without auth
            # Instead, we'll implement a fallback mechanism
            
            logger.info("Webhook message refresh attempted")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh webhook messages: {e}")
            return False

    @staticmethod
    def is_chunk_expired(chunk_data: dict, hours: int = 24) -> bool:
        """Check if chunk is older than specified hours"""
        try:
            # This would require storing timestamp in chunk_data
            # For now, we'll check the CDN URL validity instead
            return False
        except Exception as e:
            logger.error(f"Error checking chunk expiry: {e}")
            return False

    @staticmethod
    def test_cdn_url(cdn_url: str) -> bool:
        """Test if CDN URL is still valid"""
        try:
            response = requests.head(cdn_url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    @staticmethod
    def validate_chunk_urls(chunks: list) -> tuple:
        """
        Validate all chunk URLs and return (valid_chunks, invalid_chunks)
        """
        valid = []
        invalid = []
        
        for chunk in chunks:
            cdn_url = chunk.get('cdn_url')
            if cdn_url and WebhookMessageRefresh.test_cdn_url(cdn_url):
                valid.append(chunk)
            else:
                invalid.append(chunk)
        
        return valid, invalid
