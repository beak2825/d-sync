"""Compression/decompression utilities for d-sync"""

import zlib
from .config import COMPRESSION_LEVEL


class CompressionManager:
    """Manages file compression and decompression"""

    def __init__(self, level=COMPRESSION_LEVEL):
        self.level = level

    def compress_data(self, data: bytes) -> bytes:
        """Compress data using zlib"""
        return zlib.compress(data, self.level)

    def decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompress data using zlib"""
        return zlib.decompress(compressed_data)

    def compress_file(self, file_path) -> bytes:
        """Compress entire file and return compressed bytes"""
        with open(file_path, 'rb') as f:
            data = f.read()
        return self.compress_data(data)

    def decompress_file(self, compressed_data: bytes, output_path):
        """Decompress data and write to file"""
        decompressed_data = self.decompress_data(compressed_data)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decompressed_data)
