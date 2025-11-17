#!/usr/bin/env python3
"""
Unit tests for Jupyter kernel autocomplete functionality
Tests the do_complete() method and integration with C++ autocomplete bridge
"""

import sys
import os
import unittest
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import kernel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ariane-xml-jupyter-kernel'))

from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel


class TestKernelAutocomplete(unittest.TestCase):
    """Test cases for kernel autocomplete functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        # Enable DSN mode for tests
        self.kernel.dsn_mode = True
        self.kernel.dsn_version = 'AUTO'

    def test_get_partial_word_simple(self):
        """Test _get_partial_word with simple input"""
        code = "SELECT S21_"
        cursor_pos = 11  # After "S21_"
        partial = self.kernel._get_partial_word(code, cursor_pos)
        self.assertEqual(partial, "S21_")

    def test_get_partial_word_middle(self):
        """Test _get_partial_word in middle of word"""
        code = "SELECT S21_G00_30"
        cursor_pos = 11  # After "S21_G"
        partial = self.kernel._get_partial_word(code, cursor_pos)
        self.assertEqual(partial, "S21_G")

    def test_get_partial_word_start(self):
        """Test _get_partial_word at start"""
        code = "SELECT"
        cursor_pos = 0
        partial = self.kernel._get_partial_word(code, cursor_pos)
        self.assertEqual(partial, "")

    def test_get_partial_word_with_numbers(self):
        """Test _get_partial_word with numbers"""
        code = "SELECT 30_001"
        cursor_pos = 10  # After "30_"
        partial = self.kernel._get_partial_word(code, cursor_pos)
        self.assertEqual(partial, "30_")

    def test_do_complete_not_in_dsn_mode(self):
        """Test do_complete returns empty when not in DSN mode"""
        self.kernel.dsn_mode = False
        result = self.kernel.do_complete("SELECT S21_", 11)

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['matches'], [])
        self.assertEqual(result['cursor_start'], 11)
        self.assertEqual(result['cursor_end'], 11)

    @patch('subprocess.run')
    def test_do_complete_successful(self, mock_run):
        """Test do_complete with successful C++ response"""
        # Mock subprocess response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {
                "completion": "S21_G00_30",
                "display": "S21_G00_30 (INDIVIDU)",
                "description": "Bloc INDIVIDU",
                "type": "bloc"
            },
            {
                "completion": "S21_G00_40",
                "display": "S21_G00_40 (Contrat)",
                "description": "Bloc Contrat",
                "type": "bloc"
            }
        ])
        mock_run.return_value = mock_result

        result = self.kernel.do_complete("SELECT S21_", 11)

        # Check result structure
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['matches']), 2)
        self.assertIn("S21_G00_30", result['matches'])
        self.assertIn("S21_G00_40", result['matches'])

        # Check cursor positions
        self.assertEqual(result['cursor_start'], 7)  # Start of "S21_"
        self.assertEqual(result['cursor_end'], 11)   # End of "S21_"

        # Check metadata
        self.assertIn('_jupyter_types_experimental', result['metadata'])

    @patch('subprocess.run')
    def test_do_complete_with_version(self, mock_run):
        """Test do_complete passes version parameter"""
        self.kernel.dsn_version = 'P26'

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"
        mock_run.return_value = mock_result

        self.kernel.do_complete("SELECT", 6)

        # Check that version parameter was passed
        call_args = mock_run.call_args[0][0]
        self.assertIn('--version', call_args)
        self.assertIn('P26', call_args)

    @patch('subprocess.run')
    def test_do_complete_handles_error(self, mock_run):
        """Test do_complete handles C++ errors gracefully"""
        # Mock subprocess error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Schema not found"
        mock_run.return_value = mock_result

        result = self.kernel.do_complete("SELECT S21_", 11)

        # Should return empty matches, not raise exception
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['matches'], [])

    @patch('subprocess.run')
    def test_do_complete_handles_timeout(self, mock_run):
        """Test do_complete handles timeout gracefully"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 2)

        result = self.kernel.do_complete("SELECT S21_", 11)

        # Should return empty matches, not raise exception
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['matches'], [])

    @patch('subprocess.run')
    def test_do_complete_handles_invalid_json(self, mock_run):
        """Test do_complete handles invalid JSON gracefully"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_run.return_value = mock_result

        result = self.kernel.do_complete("SELECT S21_", 11)

        # Should return empty matches, not raise exception
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['matches'], [])

    @patch('subprocess.run')
    def test_do_complete_empty_suggestions(self, mock_run):
        """Test do_complete with empty suggestions from C++"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"
        mock_run.return_value = mock_result

        result = self.kernel.do_complete("SELECT XYZ", 10)

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['matches'], [])
        self.assertEqual(result['cursor_start'], 7)  # Start of "XYZ"
        self.assertEqual(result['cursor_end'], 10)   # End of "XYZ"

    @patch('subprocess.run')
    def test_do_complete_metadata_format(self, mock_run):
        """Test do_complete metadata format"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {
                "completion": "S21_G00_30_001",
                "display": "S21_G00_30_001 (NIR)",
                "description": "Numéro d'inscription au répertoire",
                "type": "field"
            }
        ])
        mock_run.return_value = mock_result

        result = self.kernel.do_complete("SELECT S21_", 11)

        # Check metadata structure
        metadata = result['metadata']['_jupyter_types_experimental']
        self.assertEqual(len(metadata), 1)

        first_item = metadata[0]
        self.assertEqual(first_item['text'], "S21_G00_30_001")
        self.assertEqual(first_item['type'], "field")
        self.assertEqual(first_item['start'], 7)
        self.assertEqual(first_item['end'], 11)


class TestIntegrationAutocomplete(unittest.TestCase):
    """Integration tests that require built C++ executable"""

    def setUp(self):
        """Check if C++ executable exists"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True

        if not os.path.exists(self.kernel.ariane_xml_path):
            self.skipTest(f"C++ executable not found at {self.kernel.ariane_xml_path}")

    def test_autocomplete_integration_basic(self):
        """Test basic autocomplete integration with C++ backend"""
        result = self.kernel.do_complete("SELECT S21_", 11)

        # Should succeed and return suggestions (if schema is available)
        self.assertEqual(result['status'], 'ok')
        self.assertIsInstance(result['matches'], list)

        # If we got matches, verify they start with S21_
        if result['matches']:
            for match in result['matches']:
                self.assertTrue(match.startswith('S21_'),
                    f"Match '{match}' should start with 'S21_'")

    def test_autocomplete_integration_keyword(self):
        """Test keyword completion integration"""
        result = self.kernel.do_complete("SEL", 3)

        self.assertEqual(result['status'], 'ok')
        # Should get SELECT keyword suggestion
        if result['matches']:
            self.assertIn('SELECT', result['matches'])


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKernelAutocomplete))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationAutocomplete))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
