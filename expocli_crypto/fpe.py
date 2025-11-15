"""
Format-Preserving Encryption (FPE) for numeric identifiers.
Uses FF3-1 algorithm for encrypting numeric strings while preserving format.
"""

import hashlib
from ff3 import FF3Cipher
from typing import Optional


class FPEEncryptor:
    """Format-preserving encryption for numeric data."""

    def __init__(self, password: str, tweak: str = "expocli"):
        """
        Initialize FPE encryptor.

        Args:
            password: Password for key derivation
            tweak: Additional parameter for FF3 (must be 8 bytes hex)
        """
        # Derive a 256-bit key from password using PBKDF2
        key_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'expocli_salt',
            100000,
            dklen=32
        )
        self.key = key_bytes.hex()

        # Ensure tweak is 8 bytes (16 hex chars)
        tweak_bytes = hashlib.sha256(tweak.encode('utf-8')).digest()[:8]
        self.tweak = tweak_bytes.hex()

        # Create FF3 cipher instance
        self.cipher = FF3Cipher(self.key, self.tweak)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a numeric string using FPE.

        Args:
            plaintext: Numeric string to encrypt

        Returns:
            Encrypted numeric string with same length and format
        """
        if not plaintext:
            return plaintext

        # Handle alphanumeric NIR (can contain letters for Corsica-born)
        # For FF3, we need to work with numeric-only strings
        # We'll preserve non-numeric characters in their positions

        # Extract only numeric characters
        numeric_only = ''.join(c for c in plaintext if c.isdigit())

        if len(numeric_only) < 6:
            # FF3 requires minimum length, use simple substitution for very short strings
            return self._simple_encrypt(plaintext)

        try:
            # Encrypt the numeric portion
            encrypted_numeric = self.cipher.encrypt(numeric_only)

            # Reconstruct with original non-numeric characters
            result = []
            numeric_idx = 0
            for char in plaintext:
                if char.isdigit():
                    result.append(encrypted_numeric[numeric_idx])
                    numeric_idx += 1
                else:
                    result.append(char)

            return ''.join(result)

        except Exception as e:
            # Fallback to simple encryption if FF3 fails
            print(f"FPE encryption failed for '{plaintext}': {e}, using fallback")
            return self._simple_encrypt(plaintext)

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a numeric string using FPE.

        Args:
            ciphertext: Encrypted numeric string

        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ciphertext

        # Extract only numeric characters
        numeric_only = ''.join(c for c in ciphertext if c.isdigit())

        if len(numeric_only) < 6:
            return self._simple_decrypt(ciphertext)

        try:
            # Decrypt the numeric portion
            decrypted_numeric = self.cipher.decrypt(numeric_only)

            # Reconstruct with original non-numeric characters
            result = []
            numeric_idx = 0
            for char in ciphertext:
                if char.isdigit():
                    result.append(decrypted_numeric[numeric_idx])
                    numeric_idx += 1
                else:
                    result.append(char)

            return ''.join(result)

        except Exception as e:
            print(f"FPE decryption failed for '{ciphertext}': {e}, using fallback")
            return self._simple_decrypt(ciphertext)

    def _simple_encrypt(self, plaintext: str) -> str:
        """Simple digit substitution for short strings."""
        # Create a deterministic substitution based on the key
        key_hash = int(hashlib.sha256(self.key.encode()).hexdigest(), 16)
        mapping = self._create_digit_mapping(key_hash)

        result = []
        for char in plaintext:
            if char.isdigit():
                result.append(mapping[int(char)])
            else:
                result.append(char)
        return ''.join(result)

    def _simple_decrypt(self, ciphertext: str) -> str:
        """Simple digit substitution reversal for short strings."""
        key_hash = int(hashlib.sha256(self.key.encode()).hexdigest(), 16)
        mapping = self._create_digit_mapping(key_hash)
        reverse_mapping = {v: str(k) for k, v in enumerate(mapping)}

        result = []
        for char in ciphertext:
            if char.isdigit():
                result.append(reverse_mapping[char])
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def _create_digit_mapping(seed: int) -> dict:
        """Create a deterministic digit substitution mapping."""
        import random
        rng = random.Random(seed)
        digits = list('0123456789')
        shuffled = digits.copy()
        rng.shuffle(shuffled)
        return shuffled
