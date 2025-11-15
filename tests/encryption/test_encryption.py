"""
Tests for the encryption module.
"""

import unittest
import tempfile
import os
from pathlib import Path

from expocli_crypto.config import EncryptionConfig, AttributeRule
from expocli_crypto.fpe import FPEEncryptor
from expocli_crypto.pseudonymizer import Pseudonymizer
from expocli_crypto.mapping_table import MappingTable
from expocli_crypto.encryptor import XMLEncryptor


class TestAttributeRule(unittest.TestCase):
    """Test attribute pattern matching."""

    def test_exact_match(self):
        """Test exact attribute matching."""
        rule = AttributeRule(pattern="30.001", encryption_type="fpe")
        self.assertTrue(rule.matches("S10.G00.30.001"))
        self.assertTrue(rule.matches("S21.G00.30.001"))
        self.assertFalse(rule.matches("S10.G00.30.002"))
        self.assertFalse(rule.matches("S10.G00.40.001"))

    def test_range_match(self):
        """Test range attribute matching."""
        rule = AttributeRule(pattern="30.001-30.010", encryption_type="fpe")
        self.assertTrue(rule.matches("S10.G00.30.001"))
        self.assertTrue(rule.matches("S10.G00.30.005"))
        self.assertTrue(rule.matches("S10.G00.30.010"))
        self.assertFalse(rule.matches("S10.G00.30.011"))
        self.assertFalse(rule.matches("S10.G00.40.005"))

    def test_invalid_attribute(self):
        """Test invalid attribute format."""
        rule = AttributeRule(pattern="30.001", encryption_type="fpe")
        self.assertFalse(rule.matches("invalid"))
        self.assertFalse(rule.matches("30.001"))


class TestFPEEncryptor(unittest.TestCase):
    """Test Format-Preserving Encryption."""

    def setUp(self):
        self.fpe = FPEEncryptor("test-password", "test-tweak")

    def test_encrypt_decrypt_numeric(self):
        """Test FPE encryption and decryption of numeric strings."""
        plaintext = "1234567890"
        ciphertext = self.fpe.encrypt(plaintext)

        # Should be different
        self.assertNotEqual(plaintext, ciphertext)

        # Should be same length
        self.assertEqual(len(plaintext), len(ciphertext))

        # Should be numeric
        self.assertTrue(ciphertext.isdigit())

        # Should decrypt back
        decrypted = self.fpe.decrypt(ciphertext)
        self.assertEqual(plaintext, decrypted)

    def test_encrypt_alphanumeric(self):
        """Test FPE with alphanumeric (NIR with letters for Corsica)."""
        plaintext = "1A3456789012B"
        ciphertext = self.fpe.encrypt(plaintext)

        # Should preserve non-numeric characters
        self.assertEqual(ciphertext[1], 'A')
        self.assertEqual(ciphertext[12], 'B')

        # Should decrypt back
        decrypted = self.fpe.decrypt(ciphertext)
        self.assertEqual(plaintext, decrypted)

    def test_deterministic(self):
        """Test that encryption is deterministic."""
        plaintext = "1234567890"
        ciphertext1 = self.fpe.encrypt(plaintext)
        ciphertext2 = self.fpe.encrypt(plaintext)
        self.assertEqual(ciphertext1, ciphertext2)


class TestPseudonymizer(unittest.TestCase):
    """Test pseudonymization."""

    def setUp(self):
        self.pseudo = Pseudonymizer(locale="fr_FR", seed=42)

    def test_pseudonymize_name(self):
        """Test name pseudonymization."""
        original = "Jean Dupont"
        pseudonym = self.pseudo.pseudonymize_name(original)

        # Should be different
        self.assertNotEqual(original, pseudonym)

        # Should be deterministic
        pseudonym2 = self.pseudo.pseudonymize_name(original)
        self.assertEqual(pseudonym, pseudonym2)

    def test_pseudonymize_address(self):
        """Test address pseudonymization."""
        original = "12 rue de la Paix, 75001 Paris"
        pseudonym = self.pseudo.pseudonymize_address(original)

        # Should be different
        self.assertNotEqual(original, pseudonym)

        # Should be deterministic
        pseudonym2 = self.pseudo.pseudonymize_address(original)
        self.assertEqual(pseudonym, pseudonym2)

    def test_pseudonymize_date(self):
        """Test date pseudonymization."""
        original = "2000-01-15"
        pseudonym = self.pseudo.pseudonymize_date(original, variance_days=30)

        # Should be different (with high probability)
        # Note: Could be same if variance is 0, but unlikely with ±30 days

        # Should be valid date format
        from datetime import datetime
        datetime.strptime(pseudonym, "%Y-%m-%d")

        # Should be deterministic
        pseudonym2 = self.pseudo.pseudonymize_date(original, variance_days=30)
        self.assertEqual(pseudonym, pseudonym2)

    def test_empty_values(self):
        """Test handling of empty values."""
        self.assertEqual(self.pseudo.pseudonymize_name(""), "")
        self.assertEqual(self.pseudo.pseudonymize_address(""), "")
        self.assertEqual(self.pseudo.pseudonymize_date(""), "")


class TestMappingTable(unittest.TestCase):
    """Test encrypted mapping table."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.enc')
        self.temp_file.close()
        self.mapping = MappingTable("test-password", self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_add_and_get_mapping(self):
        """Test adding and retrieving mappings."""
        self.mapping.add_mapping("nir", "1234567890123", "9876543210987")
        result = self.mapping.get_mapping("nir", "1234567890123")
        self.assertEqual(result, "9876543210987")

    def test_reverse_mapping(self):
        """Test reverse lookup."""
        self.mapping.add_mapping("nir", "1234567890123", "9876543210987")
        result = self.mapping.reverse_mapping("nir", "9876543210987")
        self.assertEqual(result, "1234567890123")

    def test_save_and_load(self):
        """Test saving and loading encrypted mapping table."""
        self.mapping.add_mapping("nir", "1234567890123", "9876543210987")
        self.mapping.add_mapping("name", "Jean Dupont", "Marie Martin")
        self.mapping.save()

        # Load in new instance
        mapping2 = MappingTable("test-password", self.temp_file.name)
        self.assertEqual(mapping2.get_mapping("nir", "1234567890123"), "9876543210987")
        self.assertEqual(mapping2.get_mapping("name", "Jean Dupont"), "Marie Martin")

    def test_wrong_password(self):
        """Test that wrong password fails to decrypt."""
        self.mapping.add_mapping("nir", "1234567890123", "9876543210987")
        self.mapping.save()

        # Try to load with wrong password
        mapping2 = MappingTable("wrong-password", self.temp_file.name)
        # Should have empty mappings due to decryption failure
        self.assertEqual(mapping2.mappings, {})


class TestXMLEncryptor(unittest.TestCase):
    """Test XML encryption."""

    def setUp(self):
        # Create temporary files
        self.temp_dir = tempfile.mkdtemp()
        self.input_xml = os.path.join(self.temp_dir, "input.xml")
        self.output_xml = os.path.join(self.temp_dir, "output.xml")
        self.decrypted_xml = os.path.join(self.temp_dir, "decrypted.xml")
        self.mapping_file = os.path.join(self.temp_dir, "mapping.json.enc")

        # Create sample XML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <person S21.G00.30.001="1234567890123" S21.G00.06.001="Jean Dupont" S21.G00.11.001="2000-01-15">
        <address S21.G00.06.006="12 rue de la Paix"/>
    </person>
</root>
"""
        with open(self.input_xml, 'w') as f:
            f.write(xml_content)

        # Create config
        self.config = EncryptionConfig()
        self.config.mapping_table_path = self.mapping_file
        self.config.rules = [
            AttributeRule(pattern="30.001", encryption_type="fpe"),
            AttributeRule(pattern="06.001", encryption_type="faker_name"),
            AttributeRule(pattern="06.006", encryption_type="faker_street"),
            AttributeRule(pattern="11.001", encryption_type="date_pseudo", date_variance_days=30),
        ]

    def tearDown(self):
        # Clean up
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_encrypt_and_decrypt(self):
        """Test full encryption and decryption cycle."""
        # Encrypt
        encryptor = XMLEncryptor(self.config, "test-password")
        encrypt_stats = encryptor.encrypt_file(self.input_xml, self.output_xml)

        # Check statistics
        self.assertGreater(encrypt_stats['encrypted_attributes'], 0)
        self.assertEqual(encrypt_stats['encrypted_attributes'], 4)

        # Read encrypted XML
        from lxml import etree
        tree = etree.parse(self.output_xml)
        root = tree.getroot()
        person = root.find('person')

        # Verify values are changed
        nir_encrypted = person.get('S21.G00.30.001')
        name_encrypted = person.get('S21.G00.06.001')

        self.assertNotEqual(nir_encrypted, "1234567890123")
        self.assertNotEqual(name_encrypted, "Jean Dupont")

        # Decrypt
        decryptor = XMLEncryptor(self.config, "test-password")
        decrypt_stats = decryptor.decrypt_file(self.output_xml, self.decrypted_xml)

        # Read decrypted XML
        tree = etree.parse(self.decrypted_xml)
        root = tree.getroot()
        person = root.find('person')

        # Verify values are restored
        nir_decrypted = person.get('S21.G00.30.001')
        name_decrypted = person.get('S21.G00.06.001')

        self.assertEqual(nir_decrypted, "1234567890123")
        self.assertEqual(name_decrypted, "Jean Dupont")


if __name__ == '__main__':
    unittest.main()
