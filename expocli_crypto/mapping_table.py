"""
Encrypted mapping table for reversibility.
Stores original -> encrypted mappings in an encrypted JSON file.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64


class MappingTable:
    """Manages encrypted mapping of original to pseudonymized values."""

    def __init__(self, password: str, file_path: str = "encryption_mapping.json.enc"):
        """
        Initialize mapping table.

        Args:
            password: Password for encrypting the mapping table
            file_path: Path to the encrypted mapping file
        """
        self.file_path = file_path
        self.mappings: Dict[str, Dict[str, str]] = {}

        # Derive encryption key from password using PBKDF2
        self.key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'expocli_mapping_salt',
            100000,
            dklen=32
        )

        # Load existing mappings if file exists
        if Path(file_path).exists():
            self.load()

    def add_mapping(self, category: str, original: str, encrypted: str):
        """
        Add a mapping entry.

        Args:
            category: Category of data (e.g., "nir", "name", "address")
            original: Original value
            encrypted: Encrypted/pseudonymized value
        """
        if category not in self.mappings:
            self.mappings[category] = {}

        self.mappings[category][original] = encrypted

    def get_mapping(self, category: str, original: str) -> str:
        """
        Get the encrypted value for an original value.

        Args:
            category: Category of data
            original: Original value

        Returns:
            Encrypted value or None if not found
        """
        if category in self.mappings:
            return self.mappings[category].get(original)
        return None

    def reverse_mapping(self, category: str, encrypted: str) -> str:
        """
        Get the original value for an encrypted value.

        Args:
            category: Category of data
            encrypted: Encrypted value

        Returns:
            Original value or None if not found
        """
        if category in self.mappings:
            for original, enc in self.mappings[category].items():
                if enc == encrypted:
                    return original
        return None

    def save(self):
        """Save the mapping table to encrypted file."""
        # Convert mappings to JSON
        json_data = json.dumps(self.mappings, ensure_ascii=False, indent=2)
        json_bytes = json_data.encode('utf-8')

        # Encrypt the JSON data
        encrypted_data = self._encrypt_data(json_bytes)

        # Save to file
        with open(self.file_path, 'wb') as f:
            f.write(encrypted_data)

    def load(self):
        """Load the mapping table from encrypted file."""
        try:
            # Read encrypted data
            with open(self.file_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            json_bytes = self._decrypt_data(encrypted_data)

            # Parse JSON
            self.mappings = json.loads(json_bytes.decode('utf-8'))

        except Exception as e:
            print(f"Warning: Could not load mapping table: {e}")
            self.mappings = {}

    def _encrypt_data(self, plaintext: bytes) -> bytes:
        """
        Encrypt data using AES-256-CBC.

        Args:
            plaintext: Data to encrypt

        Returns:
            Encrypted data (IV + ciphertext)
        """
        # Generate random IV
        import os
        iv = os.urandom(16)

        # Pad the plaintext
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        # Encrypt
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Return IV + ciphertext
        return iv + ciphertext

    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using AES-256-CBC.

        Args:
            encrypted_data: IV + ciphertext

        Returns:
            Decrypted plaintext
        """
        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Decrypt
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext

    def export_plaintext(self, output_path: str):
        """
        Export mapping table to plaintext JSON (for debugging/verification).

        Args:
            output_path: Path to save plaintext JSON
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, ensure_ascii=False, indent=2)

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the mapping table."""
        stats = {}
        for category, mappings in self.mappings.items():
            stats[category] = len(mappings)
        return stats
