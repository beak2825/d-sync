"""File hashing utilities for d-sync"""

import hashlib
from pathlib import Path
from typing import Tuple
from .config import CHUNK_SIZE


class HashManager:
    """Manages file hashing operations"""

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def calculate_data_hash(data: bytes) -> str:
        """Calculate SHA256 hash of bytes"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def calculate_chunk_hash(data: bytes) -> str:
        """Calculate SHA256 hash of a chunk"""
        return hashlib.sha256(data).hexdigest()
