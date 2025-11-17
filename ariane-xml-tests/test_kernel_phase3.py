#!/usr/bin/env python3
"""
Tests for Ariane-XML Jupyter Kernel - Phase 3 Features

Tests:
1. Cell Magic (%%dsn_query)
2. DataFrame Integration
3. Template Management (SAVE, DELETE, EXPORT, IMPORT)
4. Export Functionality
5. Progress Indicators
"""

import unittest
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path to import kernel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ariane-xml-jupyter-kernel'))

from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel


class TestPhase3Features(unittest.TestCase):
    """Test Phase 3 advanced features"""

    def setUp(self):
        """Set up test environment"""
        self.kernel = ArianeXMLKernel()
        # Create temporary workspace for testing
        self.test_workspace = tempfile.mkdtemp()
        self.kernel.workspace_dir = self.test_workspace
        self.kernel.templates_dir = os.path.join(self.test_workspace, 'templates')
        os.makedirs(self.kernel.templates_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)

    # ========================================================================
    # Cell Magic Tests
    # ========================================================================

    def test_parse_cell_magic_basic(self):
        """Test basic cell magic parsing"""
        code = """%%dsn_query
SELECT 01_001 FROM test.xml"""

        result = self.kernel._parse_cell_magic(code)
        self.assertIsNotNone(result)
        args, query = result
        self.assertEqual(args, {})
        self.assertEqual(query.strip(), "SELECT 01_001 FROM test.xml")

    def test_parse_cell_magic_with_args(self):
        """Test cell magic parsing with arguments"""
        code = """%%dsn_query --version P26 --output dataframe
SELECT 01_001, 01_003 FROM test.xml"""

        result = self.kernel._parse_cell_magic(code)
        self.assertIsNotNone(result)
        args, query = result
        self.assertEqual(args['version'], 'P26')
        self.assertEqual(args['output'], 'dataframe')
        self.assertIn("SELECT", query)

    def test_parse_cell_magic_not_magic(self):
        """Test that regular queries return None"""
        code = "SELECT 01_001 FROM test.xml"
        result = self.kernel._parse_cell_magic(code)
        self.assertIsNone(result)

    def test_convert_to_dataframe(self):
        """Test DataFrame conversion from pipe-separated output"""
        output = """name | age | city
John | 30 | Paris
Jane | 25 | Lyon"""

        df = self.kernel._convert_to_dataframe(output)

        # Check if pandas is available
        try:
            import pandas as pd
            self.assertIsNotNone(df)
            self.assertEqual(len(df), 2)
            self.assertEqual(list(df.columns), ['name', 'age', 'city'])
            self.assertEqual(df.iloc[0]['name'], 'John')
        except ImportError:
            self.assertIsNone(df)

    def test_convert_to_dataframe_with_separator(self):
        """Test DataFrame conversion with separator line"""
        output = """name | age | city
----|-----|-----
John | 30 | Paris
Jane | 25 | Lyon"""

        df = self.kernel._convert_to_dataframe(output)

        try:
            import pandas as pd
            self.assertIsNotNone(df)
            self.assertEqual(len(df), 2)
        except ImportError:
            self.assertIsNone(df)

    # ========================================================================
    # Template Management Tests
    # ========================================================================

    def test_save_user_template(self):
        """Test saving a user template"""
        # Add a query to history first
        self.kernel._add_to_history(
            query="SELECT 01_001 FROM test.xml",
            execution_time=0.5,
            success=True,
            row_count=10
        )

        result = self.kernel._save_user_template('my_template')

        self.assertTrue(result['success'])
        self.assertIsNone(result['error'])

        # Check that template file was created
        template_file = os.path.join(self.kernel.templates_dir, 'my_template.json')
        self.assertTrue(os.path.exists(template_file))

        # Verify template content
        with open(template_file, 'r') as f:
            template_data = json.load(f)
            self.assertEqual(template_data['name'], 'my_template')
            self.assertEqual(template_data['query'], 'SELECT 01_001 FROM test.xml')

    def test_save_template_no_history(self):
        """Test saving template with no query history"""
        result = self.kernel._save_user_template('my_template')

        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('No query to save', result['error'])

    def test_delete_user_template(self):
        """Test deleting a user template"""
        # Create a template first
        template_data = {
            'name': 'test_template',
            'query': 'SELECT * FROM test.xml'
        }
        template_file = os.path.join(self.kernel.templates_dir, 'test_template.json')
        with open(template_file, 'w') as f:
            json.dump(template_data, f)

        # Now delete it
        result = self.kernel._delete_user_template('test_template')

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(template_file))

    def test_delete_nonexistent_template(self):
        """Test deleting a template that doesn't exist"""
        result = self.kernel._delete_user_template('nonexistent')

        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'])

    def test_export_templates(self):
        """Test exporting all user templates"""
        # Create some templates
        templates = [
            {'name': 'template1', 'query': 'SELECT 01_001 FROM test1.xml'},
            {'name': 'template2', 'query': 'SELECT 01_002 FROM test2.xml'}
        ]

        for template in templates:
            template_file = os.path.join(self.kernel.templates_dir, f"{template['name']}.json")
            with open(template_file, 'w') as f:
                json.dump(template, f)

        # Export templates
        result = self.kernel._export_templates()

        self.assertTrue(result['success'])

        # Check export file was created
        export_file = os.path.join(self.test_workspace, 'templates_export.json')
        self.assertTrue(os.path.exists(export_file))

        # Verify content
        with open(export_file, 'r') as f:
            exported = json.load(f)
            self.assertEqual(len(exported), 2)

    def test_export_templates_empty(self):
        """Test exporting when no templates exist"""
        result = self.kernel._export_templates()

        self.assertFalse(result['success'])
        self.assertIn('No user templates', result['error'])

    def test_import_templates(self):
        """Test importing templates from file"""
        # Create import file
        templates = [
            {'name': 'imported1', 'query': 'SELECT 01_001 FROM test1.xml'},
            {'name': 'imported2', 'query': 'SELECT 01_002 FROM test2.xml'}
        ]

        import_file = os.path.join(self.test_workspace, 'import.json')
        with open(import_file, 'w') as f:
            json.dump(templates, f)

        # Import templates
        result = self.kernel._import_templates(import_file)

        self.assertTrue(result['success'])

        # Check templates were created
        self.assertTrue(os.path.exists(os.path.join(self.kernel.templates_dir, 'imported1.json')))
        self.assertTrue(os.path.exists(os.path.join(self.kernel.templates_dir, 'imported2.json')))

    def test_import_templates_file_not_found(self):
        """Test importing from nonexistent file"""
        result = self.kernel._import_templates('nonexistent.json')

        self.assertFalse(result['success'])
        self.assertIn('File not found', result['error'])

    # ========================================================================
    # Export Functionality Tests
    # ========================================================================

    def test_create_export_buttons(self):
        """Test export buttons HTML generation"""
        result_id = "test_123"
        html = self.kernel._create_export_buttons(result_id)

        self.assertIn('Export CSV', html)
        self.assertIn('Export JSON', html)
        self.assertIn('Export HTML', html)
        self.assertIn(f'exportData_{result_id}', html)
        self.assertIn(f'result_table_{result_id}', html)
        self.assertIn('tableToCSV', html)
        self.assertIn('tableToJSON', html)

    # ========================================================================
    # Progress Indicator Tests
    # ========================================================================

    def test_create_progress_widget(self):
        """Test progress widget creation"""
        widget = self.kernel._create_progress_widget("Testing...")

        # Widget creation depends on ipywidgets availability
        # If available, widget should be a dict with progress, label, box
        # If not available, should return None
        if widget is not None:
            self.assertIn('progress', widget)
            self.assertIn('label', widget)
            self.assertIn('box', widget)

    def test_update_progress(self):
        """Test progress widget update"""
        widget = self.kernel._create_progress_widget("Testing...")

        # Update should not raise error even if widget is None
        self.kernel._update_progress(widget, 50, "Half done")
        self.kernel._update_progress(None, 100, "Complete")

    # ========================================================================
    # Integration Tests
    # ========================================================================

    def test_template_command_integration(self):
        """Test template commands through _handle_template_command_phase3"""
        # Add query to history
        self.kernel._add_to_history(
            query="SELECT 01_001 FROM test.xml",
            execution_time=0.5,
            success=True,
            row_count=10
        )

        # Test TEMPLATE SAVE
        result = self.kernel._handle_template_command_phase3("TEMPLATE SAVE test_int")
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])

        # Test TEMPLATE DELETE
        result = self.kernel._handle_template_command_phase3("TEMPLATE DELETE test_int")
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])

    def test_html_table_with_export_buttons(self):
        """Test HTML table generation includes export buttons"""
        lines = [
            "name | age | city",
            "John | 30 | Paris",
            "Jane | 25 | Lyon"
        ]

        html = self.kernel._create_html_table(lines)

        # Should include export buttons
        self.assertIn('Export CSV', html)
        self.assertIn('Export JSON', html)
        self.assertIn('Export HTML', html)

        # Should have table with ID
        self.assertIn('id="result_table_', html)
        self.assertIn('<table', html)
        self.assertIn('</table>', html)


class TestPhase3ErrorHandling(unittest.TestCase):
    """Test error handling in Phase 3 features"""

    def setUp(self):
        """Set up test environment"""
        self.kernel = ArianeXMLKernel()
        self.test_workspace = tempfile.mkdtemp()
        self.kernel.workspace_dir = self.test_workspace
        self.kernel.templates_dir = os.path.join(self.test_workspace, 'templates')
        os.makedirs(self.kernel.templates_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_workspace):
            shutil.rmtree(self.test_workspace)

    def test_convert_to_dataframe_invalid_data(self):
        """Test DataFrame conversion with invalid data"""
        output = "This is not a table"
        df = self.kernel._convert_to_dataframe(output)

        # Should return None for invalid data
        self.assertIsNone(df)

    def test_import_templates_invalid_json(self):
        """Test importing templates with invalid JSON"""
        import_file = os.path.join(self.test_workspace, 'invalid.json')
        with open(import_file, 'w') as f:
            f.write("This is not valid JSON")

        result = self.kernel._import_templates(import_file)

        self.assertFalse(result['success'])
        self.assertIn('Failed to import', result['error'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
