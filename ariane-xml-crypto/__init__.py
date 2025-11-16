"""
Ariane-XML Encryption Module

This module provides encryption and pseudonymization capabilities for XML data,
specifically designed for French administrative data with support for:
- Format-preserving encryption (FPE) for numeric IDs (NIR, SIREN, SIRET)
- Faker-based pseudonymization for French names and addresses
- Date pseudonymization with age range preservation
- Encrypted mapping tables for reversibility
"""

__version__ = "1.0.0"
__author__ = "Ariane-XML Team"

from .encryptor import XMLEncryptor
from .config import EncryptionConfig

__all__ = ["XMLEncryptor", "EncryptionConfig"]
