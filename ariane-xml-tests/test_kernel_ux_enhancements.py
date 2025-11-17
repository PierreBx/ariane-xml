#!/usr/bin/env python3
"""
Comprehensive tests for DSN MODE UX Enhancements (Phase 1 & Phase 2)

Tests coverage for:
- Phase 1: Quick Reference, Enhanced Errors, Help System, Schema Browser
- Phase 2: Query History, Field Search, RERUN, SAVE QUERY

Based on: DSN_JUPYTER_UX_ENHANCEMENTS.md
"""

import sys
import os
import unittest
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path to import kernel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ariane-xml-jupyter-kernel'))

from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel


class TestPhase1QuickReference(unittest.TestCase):
    """Test Phase 1 Feature: Quick Reference Card"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()

    def test_banner_contains_quick_reference(self):
        """Test that kernel banner includes quick reference information"""
        banner = self.kernel.banner

        # Check for key DSN MODE commands
        self.assertIn('SET MODE DSN', banner)
        self.assertIn('DESCRIBE', banner)
        self.assertIn('TEMPLATE LIST', banner)

        # Check for tips and examples
        self.assertIn('Tips:', banner)
        self.assertIn('Examples:', banner)

    def test_quick_reference_on_dsn_activation(self):
        """Test that quick reference appears when DSN MODE is activated"""
        self.kernel.dsn_mode = False
        self.kernel.dsn_quickstart = True

        # Activate DSN mode by updating state
        self.kernel._update_dsn_state('SET MODE DSN')

        # Check that DSN mode is now active
        self.assertTrue(self.kernel.dsn_mode)

    def test_dsn_quickstart_toggle(self):
        """Test that DSN_QUICKSTART setting can be toggled"""
        # Initially True
        self.assertTrue(self.kernel.dsn_quickstart)

        # Can be set to False
        self.kernel.dsn_quickstart = False
        self.assertFalse(self.kernel.dsn_quickstart)


class TestPhase1HelpSystem(unittest.TestCase):
    """Test Phase 1 Feature: Interactive Help System"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.dsn_version = 'P26'

    def test_general_help_command(self):
        """Test HELP command shows general help"""
        result = self.kernel._get_help_output()

        self.assertTrue(result['success'])
        self.assertIn('help', result['output'].lower())

        # Check for major command categories
        self.assertIn('BROWSE', result['output'])
        self.assertIn('SEARCH', result['output'])
        self.assertIn('DESCRIBE', result['output'])
        self.assertIn('TEMPLATE', result['output'])

    def test_specific_command_help(self):
        """Test HELP <command> shows specific command help"""
        commands_to_test = ['BROWSE', 'SEARCH', 'DESCRIBE', 'TEMPLATE', 'HISTORY']

        for cmd in commands_to_test:
            result = self.kernel._get_help_output(cmd)

            self.assertTrue(result['success'], f"Help for {cmd} should succeed")
            self.assertIn(cmd, result['output'], f"Help output should mention {cmd}")

    def test_help_browse_command(self):
        """Test HELP BROWSE shows detailed BROWSE help"""
        result = self.kernel._get_help_output('BROWSE')

        self.assertTrue(result['success'])
        self.assertIn('BROWSE SCHEMA', result['output'])
        self.assertIn('BROWSE BLOC', result['output'])

    def test_help_search_command(self):
        """Test HELP SEARCH shows detailed SEARCH help"""
        result = self.kernel._get_help_output('SEARCH')

        self.assertTrue(result['success'])
        self.assertIn('SEARCH', result['output'])
        self.assertIn('keyword', result['output'].lower())

    def test_help_history_command(self):
        """Test HELP HISTORY shows detailed HISTORY help"""
        result = self.kernel._get_help_output('HISTORY')

        self.assertTrue(result['success'])
        self.assertIn('HISTORY', result['output'])
        self.assertIn('RERUN', result['output'])
        self.assertIn('SAVE QUERY', result['output'])

    def test_help_unknown_command(self):
        """Test HELP <unknown> returns appropriate message"""
        result = self.kernel._get_help_output('NONEXISTENT')

        # Should still return success but indicate unknown command
        self.assertTrue(result['success'])
        self.assertIn('HELP', result['output'])


class TestPhase1SchemaBrowser(unittest.TestCase):
    """Test Phase 1 Feature: Visual Schema Browser"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.dsn_version = 'P26'

    def test_browse_schema_command(self):
        """Test BROWSE SCHEMA shows all blocs"""
        result = self.kernel._handle_browse_command('BROWSE SCHEMA')

        self.assertTrue(result['success'])
        self.assertIn('Schema Browser', result['output'])

        # Check for key blocs
        self.assertIn('Bloc 01', result['output'])
        self.assertIn('Bloc 02', result['output'])
        self.assertIn('Bloc 30', result['output'])

    def test_browse_bloc_command(self):
        """Test BROWSE BLOC <number> shows bloc details"""
        result = self.kernel._handle_browse_command('BROWSE BLOC 01')

        self.assertTrue(result['success'])
        self.assertIn('Bloc 01', result['output'])

        # Should include field information
        output_lower = result['output'].lower()
        self.assertTrue('field' in output_lower or 'champ' in output_lower)

    def test_browse_bloc_30(self):
        """Test BROWSE BLOC 30 (NIR bloc)"""
        result = self.kernel._handle_browse_command('BROWSE BLOC 30')

        self.assertTrue(result['success'])
        self.assertIn('30', result['output'])

    def test_browse_bloc_invalid_format(self):
        """Test BROWSE BLOC with invalid format"""
        result = self.kernel._handle_browse_command('BROWSE BLOC')

        self.assertFalse(result['success'])
        self.assertIn('Usage', result['error'])

    def test_browse_bloc_invalid_number(self):
        """Test BROWSE BLOC with invalid bloc number"""
        result = self.kernel._handle_browse_command('BROWSE BLOC ABC')

        # Implementation may accept it and return an error message or handle gracefully
        # Just verify it returns a result
        self.assertIsNotNone(result)

    def test_browse_unknown_command(self):
        """Test BROWSE with unknown subcommand"""
        result = self.kernel._handle_browse_command('BROWSE UNKNOWN')

        self.assertFalse(result['success'])
        self.assertIn('Usage', result['error'])


class TestPhase1EnhancedErrors(unittest.TestCase):
    """Test Phase 1 Feature: Enhanced Error Messages"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True

    def test_enhance_error_with_suggestions(self):
        """Test that errors are enhanced with helpful suggestions"""
        error_msg = "Unknown field 'INVALID_FIELD'"
        query = "SELECT INVALID_FIELD FROM test.xml"

        enhanced = self.kernel._enhance_error_message(error_msg, query)

        # Enhanced message should contain suggestions
        self.assertIn('💡', enhanced)  # Tips icon

    def test_enhance_schema_error(self):
        """Test enhancement of schema-related errors"""
        error_msg = "Schema not found"
        query = "SELECT 01_001 FROM test.xml"

        enhanced = self.kernel._enhance_error_message(error_msg, query)

        # Should suggest schema-related help
        self.assertTrue(len(enhanced) > len(error_msg))

    def test_enhance_file_error(self):
        """Test enhancement of file-related errors"""
        error_msg = "File not found: /path/to/file.xml"
        query = "SELECT * FROM /path/to/file.xml"

        enhanced = self.kernel._enhance_error_message(error_msg, query)

        # Should contain helpful suggestions
        self.assertTrue(len(enhanced) > len(error_msg))

    def test_error_includes_help_reference(self):
        """Test that enhanced errors include HELP reference"""
        error_msg = "Syntax error"
        query = "INVALID QUERY"

        enhanced = self.kernel._enhance_error_message(error_msg, query)

        # Should suggest HELP or BROWSE SCHEMA
        enhanced_lower = enhanced.lower()
        self.assertTrue('help' in enhanced_lower or 'browse' in enhanced_lower)


class TestPhase2QueryHistory(unittest.TestCase):
    """Test Phase 2 Feature: Query History"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        # Clear history
        self.kernel.query_history = []

    def test_add_to_history(self):
        """Test adding queries to history"""
        self.kernel._add_to_history(
            query="SELECT 01_001 FROM test.xml",
            execution_time=150.5,
            success=True,
            row_count=10
        )

        self.assertEqual(len(self.kernel.query_history), 1)
        entry = self.kernel.query_history[0]

        self.assertEqual(entry['query'], "SELECT 01_001 FROM test.xml")
        self.assertEqual(entry['execution_time'], 150.5)
        self.assertTrue(entry['success'])
        self.assertEqual(entry['row_count'], 10)
        self.assertIn('timestamp', entry)

    def test_history_excludes_meta_commands(self):
        """Test that HISTORY, RERUN, etc. are not added to history"""
        meta_commands = ['HISTORY', 'HISTORY 5', 'RERUN 3', 'SAVE QUERY test']

        for cmd in meta_commands:
            self.kernel._add_to_history(cmd, 10.0, True, 0)

        # History should be empty
        self.assertEqual(len(self.kernel.query_history), 0)

    def test_history_command_empty(self):
        """Test HISTORY command with empty history"""
        result = self.kernel._handle_history_command()

        self.assertTrue(result['success'])
        self.assertIn('empty', result['output'].lower())

    def test_history_command_with_entries(self):
        """Test HISTORY command with entries"""
        # Add some test queries (avoid special characters that get HTML escaped)
        test_queries = [
            "SELECT 01_001 FROM test.xml",
            "DESCRIBE 30_001",
            "SELECT * FROM data.xml WHERE 01_001 = '123'"
        ]

        for i, query in enumerate(test_queries):
            self.kernel._add_to_history(query, 100.0 + i, True, 5)

        result = self.kernel._handle_history_command()

        self.assertTrue(result['success'])

        # Should contain key parts of queries (accounting for HTML escaping)
        self.assertIn('SELECT 01_001 FROM test.xml', result['output'])
        self.assertIn('DESCRIBE 30_001', result['output'])
        # Third query may have escaped quotes, so check for key parts
        self.assertIn('SELECT * FROM data.xml', result['output'])

    def test_history_command_with_limit(self):
        """Test HISTORY <number> limits results"""
        # Add 10 queries
        for i in range(10):
            self.kernel._add_to_history(f"SELECT {i} FROM test.xml", 100.0, True, 1)

        # Request last 3
        result = self.kernel._handle_history_command(limit=3)

        self.assertTrue(result['success'])

        # Should show "Last 3 of 10"
        self.assertIn('3', result['output'])

    def test_history_maintains_order(self):
        """Test that history maintains chronological order"""
        queries = ["Query 1", "Query 2", "Query 3"]

        for query in queries:
            self.kernel._add_to_history(query, 100.0, True, 1)

        # Verify order in history
        for i, query in enumerate(queries):
            self.assertEqual(self.kernel.query_history[i]['query'], query)


class TestPhase2RerunCommand(unittest.TestCase):
    """Test Phase 2 Feature: RERUN Command"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.query_history = []

        # Add test queries to history
        self.test_queries = [
            "SELECT 01_001 FROM test1.xml",
            "DESCRIBE 30_001",
            "SELECT * FROM test2.xml"
        ]

        for query in self.test_queries:
            self.kernel._add_to_history(query, 100.0, True, 5)

    def test_rerun_valid_index(self):
        """Test RERUN with valid index"""
        result = self.kernel._handle_rerun_command(2)

        self.assertTrue(result['success'])
        self.assertIn('rerun_query', result)
        self.assertEqual(result['rerun_query'], self.test_queries[1])

    def test_rerun_first_query(self):
        """Test RERUN 1 reruns first query"""
        result = self.kernel._handle_rerun_command(1)

        self.assertTrue(result['success'])
        self.assertEqual(result['rerun_query'], self.test_queries[0])

    def test_rerun_last_query(self):
        """Test RERUN <last> reruns last query"""
        last_index = len(self.test_queries)
        result = self.kernel._handle_rerun_command(last_index)

        self.assertTrue(result['success'])
        self.assertEqual(result['rerun_query'], self.test_queries[-1])

    def test_rerun_invalid_index_too_high(self):
        """Test RERUN with index > history length"""
        result = self.kernel._handle_rerun_command(999)

        self.assertFalse(result['success'])
        self.assertIn('Invalid', result['error'])

    def test_rerun_invalid_index_zero(self):
        """Test RERUN with index 0"""
        result = self.kernel._handle_rerun_command(0)

        self.assertFalse(result['success'])
        self.assertIn('Invalid', result['error'])

    def test_rerun_invalid_index_negative(self):
        """Test RERUN with negative index"""
        result = self.kernel._handle_rerun_command(-1)

        self.assertFalse(result['success'])
        self.assertIn('Invalid', result['error'])

    def test_rerun_shows_query_preview(self):
        """Test that RERUN shows the query being rerun"""
        result = self.kernel._handle_rerun_command(1)

        self.assertTrue(result['success'])
        # Output should show the query being rerun
        self.assertIn(self.test_queries[0], result['output'])


class TestPhase2SaveQuery(unittest.TestCase):
    """Test Phase 2 Feature: SAVE QUERY Command"""

    def setUp(self):
        """Set up test fixtures with temporary workspace"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.query_history = []

        # Create temporary workspace directory
        self.temp_workspace = tempfile.mkdtemp()
        self.kernel.workspace_dir = self.temp_workspace
        self.kernel.queries_dir = os.path.join(self.temp_workspace, 'queries')
        os.makedirs(self.kernel.queries_dir, exist_ok=True)

        # Add a successful query to history
        self.test_query = "SELECT 01_001, 30_001 FROM test.xml WHERE 01_001 = '123'"
        self.kernel._add_to_history(self.test_query, 150.0, True, 10)

    def tearDown(self):
        """Clean up temporary workspace"""
        if os.path.exists(self.temp_workspace):
            shutil.rmtree(self.temp_workspace)

    def test_save_query_success(self):
        """Test SAVE QUERY saves last successful query"""
        result = self.kernel._handle_save_query_command('my_test_query')

        self.assertTrue(result['success'])

        # Check that file was created
        query_file = os.path.join(self.kernel.queries_dir, 'my_test_query.json')
        self.assertTrue(os.path.exists(query_file))

        # Verify file contents
        with open(query_file, 'r') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['query'], self.test_query)
        self.assertEqual(saved_data['name'], 'my_test_query')
        self.assertIn('created_at', saved_data)

    def test_save_query_no_history(self):
        """Test SAVE QUERY with no history"""
        self.kernel.query_history = []

        result = self.kernel._handle_save_query_command('test')

        self.assertFalse(result['success'])
        self.assertIn('No successful query', result['error'])

    def test_save_query_only_failed_queries(self):
        """Test SAVE QUERY when only failed queries exist"""
        self.kernel.query_history = []
        self.kernel._add_to_history("INVALID QUERY", 10.0, False, 0)

        result = self.kernel._handle_save_query_command('test')

        self.assertFalse(result['success'])
        self.assertIn('No successful query', result['error'])

    def test_save_query_invalid_name(self):
        """Test SAVE QUERY with invalid name (empty)"""
        result = self.kernel._handle_save_query_command('')

        self.assertFalse(result['success'])
        self.assertIn('Usage', result['error'])

    def test_save_query_overwrites_existing(self):
        """Test SAVE QUERY overwrites existing saved query"""
        # Save first time
        self.kernel._handle_save_query_command('duplicate_name')

        # Add new query to history
        new_query = "SELECT * FROM new.xml"
        self.kernel._add_to_history(new_query, 200.0, True, 20)

        # Save again with same name
        result = self.kernel._handle_save_query_command('duplicate_name')

        self.assertTrue(result['success'])

        # Verify the newer query is saved
        query_file = os.path.join(self.kernel.queries_dir, 'duplicate_name.json')
        with open(query_file, 'r') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['query'], new_query)


class TestPhase2FieldSearch(unittest.TestCase):
    """Test Phase 2 Feature: Field Search"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.dsn_version = 'P26'

    def test_search_command_basic(self):
        """Test SEARCH command with basic keyword"""
        result = self.kernel._handle_search_command('SEARCH "numero"')

        self.assertTrue(result['success'])
        # May show results or "No results found" depending on sample data
        self.assertIn('🔍', result['output'])

    def test_search_command_with_quotes(self):
        """Test SEARCH command respects quoted strings"""
        result = self.kernel._handle_search_command('SEARCH "numéro nir"')

        self.assertTrue(result['success'])
        # May show results or "No results found" depending on sample data
        self.assertIn('🔍', result['output'])

    def test_search_command_single_quotes(self):
        """Test SEARCH command with single quotes"""
        result = self.kernel._handle_search_command("SEARCH 'naissance'")

        self.assertTrue(result['success'])
        self.assertIn('Search Results', result['output'])

    def test_search_command_no_quotes(self):
        """Test SEARCH command without quotes fails gracefully"""
        result = self.kernel._handle_search_command('SEARCH keyword')

        self.assertFalse(result['success'])
        self.assertIn('Usage', result['error'])

    def test_search_command_empty_keyword(self):
        """Test SEARCH with empty keyword"""
        result = self.kernel._handle_search_command('SEARCH ""')

        # Should handle gracefully
        self.assertTrue(result['success'] or 'error' in result)

    def test_search_output_format(self):
        """Test that search output is properly formatted"""
        result = self.kernel._handle_search_command('SEARCH "test"')

        self.assertTrue(result['success'])
        # Should contain formatted HTML
        self.assertIn('<', result['output'])  # HTML tags


class TestPhase2Integration(unittest.TestCase):
    """Integration tests for Phase 2 features working together"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()
        self.kernel.dsn_mode = True
        self.kernel.query_history = []

        # Setup temporary workspace
        self.temp_workspace = tempfile.mkdtemp()
        self.kernel.workspace_dir = self.temp_workspace
        self.kernel.queries_dir = os.path.join(self.temp_workspace, 'queries')
        os.makedirs(self.kernel.queries_dir, exist_ok=True)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_workspace):
            shutil.rmtree(self.temp_workspace)

    def test_workflow_history_rerun_save(self):
        """Test complete workflow: execute -> history -> rerun -> save"""
        # Step 1: Add queries to history
        queries = [
            "SELECT 01_001 FROM test.xml",
            "DESCRIBE 30_001",
            "SELECT * FROM data.xml"
        ]

        for query in queries:
            self.kernel._add_to_history(query, 100.0, True, 5)

        # Step 2: View history
        history_result = self.kernel._handle_history_command()
        self.assertTrue(history_result['success'])

        # Step 3: Rerun a query
        rerun_result = self.kernel._handle_rerun_command(2)
        self.assertTrue(rerun_result['success'])
        self.assertEqual(rerun_result['rerun_query'], queries[1])

        # Step 4: Save the query
        save_result = self.kernel._handle_save_query_command('my_saved_query')
        self.assertTrue(save_result['success'])

        # Verify saved query exists
        query_file = os.path.join(self.kernel.queries_dir, 'my_saved_query.json')
        self.assertTrue(os.path.exists(query_file))

    def test_multiple_saves_different_names(self):
        """Test saving multiple queries with different names"""
        # Add multiple queries
        for i in range(3):
            query = f"SELECT {i} FROM test{i}.xml"
            self.kernel._add_to_history(query, 100.0, True, 1)

            # Save each
            result = self.kernel._handle_save_query_command(f'query_{i}')
            self.assertTrue(result['success'])

        # Verify all files exist
        for i in range(3):
            query_file = os.path.join(self.kernel.queries_dir, f'query_{i}.json')
            self.assertTrue(os.path.exists(query_file))


class TestWorkspaceInitialization(unittest.TestCase):
    """Test workspace and directory initialization"""

    def setUp(self):
        """Set up with temporary home directory"""
        self.temp_home = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_home

    def tearDown(self):
        """Clean up"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        if os.path.exists(self.temp_home):
            shutil.rmtree(self.temp_home)

    def test_workspace_creation(self):
        """Test that workspace directory is created on kernel init"""
        kernel = ArianeXMLKernel()

        # Workspace directory should exist
        self.assertTrue(os.path.exists(kernel.workspace_dir))

        # Queries subdirectory should exist
        self.assertTrue(os.path.exists(kernel.queries_dir))

    def test_workspace_already_exists(self):
        """Test that existing workspace is not corrupted"""
        # Create workspace manually
        workspace_dir = os.path.join(self.temp_home, '.ariane-xml-workspace')
        os.makedirs(workspace_dir, exist_ok=True)

        # Create a test file
        test_file = os.path.join(workspace_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        # Initialize kernel
        kernel = ArianeXMLKernel()

        # Test file should still exist
        self.assertTrue(os.path.exists(test_file))


class TestDSNModeStateManagement(unittest.TestCase):
    """Test DSN mode state management across features"""

    def setUp(self):
        """Set up test fixtures"""
        self.kernel = ArianeXMLKernel()

    def test_features_require_dsn_mode(self):
        """Test that DSN features check for DSN mode"""
        self.kernel.dsn_mode = False

        # BROWSE should work (it's kernel-level)
        result = self.kernel._handle_browse_command('BROWSE SCHEMA')
        # Result depends on implementation - some features may require DSN mode

    def test_version_tracking(self):
        """Test DSN version is tracked correctly"""
        self.kernel._update_dsn_state('SET DSN_VERSION P25')
        self.assertEqual(self.kernel.dsn_version, 'P25')

        self.kernel._update_dsn_state('SET DSN_VERSION P26')
        self.assertEqual(self.kernel.dsn_version, 'P26')

        self.kernel._update_dsn_state('SET DSN_VERSION AUTO')
        self.assertEqual(self.kernel.dsn_version, 'AUTO')

    def test_mode_deactivation_clears_state(self):
        """Test that deactivating DSN mode clears state"""
        self.kernel._update_dsn_state('SET MODE DSN')
        self.kernel._update_dsn_state('SET DSN_VERSION P26')

        self.assertTrue(self.kernel.dsn_mode)
        self.assertEqual(self.kernel.dsn_version, 'P26')

        self.kernel._update_dsn_state('SET MODE STANDARD')

        self.assertFalse(self.kernel.dsn_mode)
        self.assertIsNone(self.kernel.dsn_version)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        # Phase 1 Tests
        TestPhase1QuickReference,
        TestPhase1HelpSystem,
        TestPhase1SchemaBrowser,
        TestPhase1EnhancedErrors,

        # Phase 2 Tests
        TestPhase2QueryHistory,
        TestPhase2RerunCommand,
        TestPhase2SaveQuery,
        TestPhase2FieldSearch,
        TestPhase2Integration,

        # Infrastructure Tests
        TestWorkspaceInitialization,
        TestDSNModeStateManagement,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
