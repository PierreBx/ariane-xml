"""
Main XML encryptor that coordinates all encryption operations.
"""

from lxml import etree
from typing import Optional, Dict, Any
import re
import hashlib
from datetime import datetime

from .config import EncryptionConfig, AttributeRule

# Pseudonymisation marker constants
PSEUDO_MARKER_TARGET = "ariane-pseudonymised"
PSEUDO_MARKER_VERSION = "1.0"


def is_pseudonymised(file_path: str) -> bool:
    """
    Check if an XML file has been pseudonymised by ariane-xml.

    Args:
        file_path: Path to the XML file

    Returns:
        True if the file contains the pseudonymisation marker
    """
    try:
        tree = etree.parse(file_path)
        # Look for processing instruction using XPath
        pis = tree.xpath(f'//processing-instruction("{PSEUDO_MARKER_TARGET}")')
        return len(pis) > 0
    except Exception:
        return False


def get_pseudonymisation_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """
    Get pseudonymisation metadata from an XML file.

    Args:
        file_path: Path to the XML file

    Returns:
        Dictionary with metadata (version, date, tool, config-hash) or None
    """
    try:
        tree = etree.parse(file_path)
        # Look for processing instruction using XPath
        pis = tree.xpath(f'//processing-instruction("{PSEUDO_MARKER_TARGET}")')
        if pis:
            # Parse the attributes from the PI text
            pi_text = str(pis[0])
            metadata = {}
            for match in re.finditer(r'(\w+(?:-\w+)?)="([^"]*)"', pi_text):
                metadata[match.group(1)] = match.group(2)
            return metadata
        return None
    except Exception:
        return None
from .fpe import FPEEncryptor
from .pseudonymizer import Pseudonymizer
from .mapping_table import MappingTable


class XMLEncryptor:
    """Main class for encrypting XML data."""

    def __init__(self, config: EncryptionConfig, password: str):
        """
        Initialize XML encryptor.

        Args:
            config: Encryption configuration
            password: Password for FPE and mapping table encryption
        """
        self.config = config
        self.password = password

        # Initialize encryptors
        self.fpe = FPEEncryptor(password, config.fpe_tweak)
        self.pseudonymizer = Pseudonymizer(
            locale=config.faker_locale,
            seed=config.faker_seed
        )
        self.mapping_table = MappingTable(password, config.mapping_table_path)

        # Statistics
        self.stats = {
            'total_attributes': 0,
            'encrypted_attributes': 0,
            'by_type': {}
        }

    def encrypt_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Encrypt an XML file.

        Args:
            input_path: Path to input XML file
            output_path: Path to output encrypted XML file

        Returns:
            Statistics about the encryption process
        """
        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Process all elements with attributes
        self._process_element(root)

        # Add pseudonymisation marker
        self._add_pseudonymisation_marker(root)

        # Save encrypted XML
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        )

        # Save mapping table
        self.mapping_table.save()

        return self.stats

    def _add_pseudonymisation_marker(self, root: etree.Element):
        """
        Add a processing instruction to mark the file as pseudonymised.

        Args:
            root: Root element of the XML document
        """
        # Generate config hash for traceability
        config_str = str(self.config.attributes) + str(self.config.fpe_tweak)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]

        # Build marker content
        marker_content = (
            f'version="{PSEUDO_MARKER_VERSION}" '
            f'date="{datetime.utcnow().isoformat()}Z" '
            f'tool="ariane-xml-crypto" '
            f'config-hash="{config_hash}"'
        )

        # Create processing instruction
        pi = etree.ProcessingInstruction(PSEUDO_MARKER_TARGET, marker_content)

        # Insert at the beginning (before root element)
        root.getparent().insert(0, pi)

    def decrypt_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Decrypt an XML file using the mapping table.

        Args:
            input_path: Path to encrypted XML file
            output_path: Path to output decrypted XML file

        Returns:
            Statistics about the decryption process
        """
        # Parse XML
        tree = etree.parse(input_path)
        root = tree.getroot()

        # Process all elements with attributes
        self._process_element(root, decrypt=True)

        # Save decrypted XML
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        )

        return self.stats

    def _process_element(self, element: etree.Element, decrypt: bool = False):
        """
        Recursively process an XML element and its children.
        Processes both XML attributes and element tags.

        Args:
            element: XML element to process
            decrypt: If True, decrypt instead of encrypt
        """
        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            self.stats['total_attributes'] += 1

            # Check if this attribute should be encrypted
            rule = self.config.get_rule_for_attribute(attr_name)

            if rule:
                if decrypt:
                    new_value = self._decrypt_value(attr_name, attr_value, rule)
                else:
                    new_value = self._encrypt_value(attr_name, attr_value, rule)

                element.set(attr_name, new_value)
                self.stats['encrypted_attributes'] += 1

                # Update type statistics
                enc_type = rule.encryption_type
                self.stats['by_type'][enc_type] = self.stats['by_type'].get(enc_type, 0) + 1

        # Process element tags (e.g., <S21.G00.30.001>value</S21.G00.30.001>)
        # Get the tag name without namespace
        tag_name = str(element.tag)  # Convert to string first
        if '}' in tag_name:
            tag_name = tag_name.split('}')[1]  # Remove namespace

        # Check if this element tag should be encrypted
        rule = self.config.get_rule_for_attribute(tag_name)

        if rule and element.text and element.text.strip():
            self.stats['total_attributes'] += 1

            if decrypt:
                new_value = self._decrypt_value(tag_name, element.text.strip(), rule)
            else:
                new_value = self._encrypt_value(tag_name, element.text.strip(), rule)

            element.text = new_value
            self.stats['encrypted_attributes'] += 1

            # Update type statistics
            enc_type = rule.encryption_type
            self.stats['by_type'][enc_type] = self.stats['by_type'].get(enc_type, 0) + 1

        # Process children recursively
        for child in element:
            self._process_element(child, decrypt)

    def _encrypt_value(self, attr_name: str, value: str, rule: AttributeRule) -> str:
        """
        Encrypt a single attribute value.

        Args:
            attr_name: Attribute name
            value: Original value
            rule: Encryption rule to apply

        Returns:
            Encrypted value
        """
        if not value or not value.strip():
            return value

        encrypted = value
        category = f"{attr_name}:{rule.encryption_type}"

        # Check if we already have this mapping
        existing = self.mapping_table.get_mapping(category, value)
        if existing:
            return existing

        # Apply encryption based on type
        if rule.encryption_type == "fpe":
            encrypted = self.fpe.encrypt(value)

        elif rule.encryption_type == "faker_name":
            encrypted = self.pseudonymizer.pseudonymize_name(value)

        elif rule.encryption_type == "faker_address":
            encrypted = self.pseudonymizer.pseudonymize_address(value)

        elif rule.encryption_type == "faker_street":
            encrypted = self.pseudonymizer.pseudonymize_street(value)

        elif rule.encryption_type == "faker_city":
            encrypted = self.pseudonymizer.pseudonymize_city(value)

        elif rule.encryption_type == "faker_postal_code":
            encrypted = self.pseudonymizer.pseudonymize_postal_code(value)

        elif rule.encryption_type == "faker_phone":
            encrypted = self.pseudonymizer.pseudonymize_phone(value)

        elif rule.encryption_type == "faker_email":
            encrypted = self.pseudonymizer.pseudonymize_email(value)

        elif rule.encryption_type == "faker_company":
            encrypted = self.pseudonymizer.pseudonymize_company(value)

        elif rule.encryption_type == "date_pseudo":
            encrypted = self.pseudonymizer.pseudonymize_date(
                value,
                variance_days=rule.date_variance_days
            )

        else:
            print(f"Warning: Unknown encryption type '{rule.encryption_type}' for {attr_name}")

        # Store mapping
        self.mapping_table.add_mapping(category, value, encrypted)

        return encrypted

    def _decrypt_value(self, attr_name: str, value: str, rule: AttributeRule) -> str:
        """
        Decrypt a single attribute value using the mapping table.

        Args:
            attr_name: Attribute name
            value: Encrypted value
            rule: Encryption rule that was applied

        Returns:
            Original value
        """
        if not value or not value.strip():
            return value

        category = f"{attr_name}:{rule.encryption_type}"

        # Look up in mapping table
        original = self.mapping_table.reverse_mapping(category, value)

        if original:
            return original

        # If not in mapping table, try to decrypt with FPE (for reversible encryption)
        if rule.encryption_type == "fpe":
            try:
                return self.fpe.decrypt(value)
            except Exception as e:
                print(f"Warning: Could not decrypt FPE value for {attr_name}: {e}")

        print(f"Warning: No mapping found for {attr_name} = '{value}'")
        return value

    def get_statistics(self) -> Dict[str, Any]:
        """Get encryption statistics."""
        mapping_stats = self.mapping_table.get_statistics()
        return {
            **self.stats,
            'mapping_table': mapping_stats
        }
