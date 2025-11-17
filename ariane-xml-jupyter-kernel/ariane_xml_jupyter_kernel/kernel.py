#!/usr/bin/env python3
"""
Ariane-XML Jupyter Kernel - Enhanced Version with HTML Table Output

This is a proof-of-concept enhancement showing rich HTML table formatting.
To use: Copy this over kernel.py or import specific methods.
"""

from ipykernel.kernelbase import Kernel
import subprocess
import re
import os
import time
from typing import Dict, Any, List, Optional


class ArianeXMLKernel(Kernel):
    """Enhanced Jupyter kernel for Ariane-XML with rich HTML output"""

    implementation = 'Ariane-XML'
    implementation_version = '1.1.0'
    language = 'ariane-xml-sql'
    language_version = '1.0'
    language_info = {
        'name': 'ariane-xml-sql',
        'mimetype': 'text/x-sql',
        'file_extension': '.eql',
        'codemirror_mode': 'sql',
        'pygments_lexer': 'sql'
    }
    banner = """Ariane-XML Kernel - SQL-like XML Querying 🚀

Welcome! Query XML files using familiar SQL syntax with rich HTML output.

📘 NEW TO ARIANE-XML?
   Open: ariane-xml-examples/00_Getting_Started.ipynb
   This interactive tutorial has pre-written queries to run!

✨ Features:
   • Styled HTML tables with zebra striping
   • Hover effects for better readability
   • Automatic numeric/text alignment
   • Query multiple files with wildcards (*.xml)
   • DSN MODE for French DSN files (P25/P26)

📝 Quick Example (try it now!):
   SELECT name, price FROM ariane-xml-examples/test.xml WHERE price < 6

🇫🇷 DSN MODE (for French DSN files):
   SET MODE DSN              -- Enable DSN mode
   SET DSN_VERSION P26       -- Use P26 schema
   SELECT 01_001, 01_003 FROM ./dsn.xml  -- Query with shortcuts
   DESCRIBE 01_001           -- Show field documentation
   TEMPLATE LIST             -- List query templates
   COMPARE P25 P26           -- Compare schema versions

💡 Tips:
   • Press Shift+Enter to run a cell
   • Use -- for comments in your queries
   • Type 'help' for Ariane-XML documentation
   • If nothing happens, check file paths are correct

🎓 More Examples:
   • ExpoCLI_Demo.ipynb - Complete tutorial
   • Enhanced_Tables_Demo.ipynb - Advanced formatting
"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ariane_xml_path = self._find_ariane_xml()
        self.working_directory = self._find_working_directory()

        # DSN MODE state tracking
        self.dsn_mode = False
        self.dsn_version = None  # None, 'P25', 'P26', or 'AUTO'

    def _find_ariane_xml(self) -> str:
        """Locate the Ariane-XML executable"""
        # In Docker, check the build directory first
        docker_path = '/app/ariane-xml-c-kernel/build/ariane-xml'
        if os.path.exists(docker_path):
            return docker_path

        # Check for local development build in standard locations
        local_dev_paths = [
            '/home/user/ariane-xml/ariane-xml-c-kernel/build/ariane-xml',
            os.path.expanduser('~/ariane-xml/ariane-xml-c-kernel/build/ariane-xml'),
        ]

        for path in local_dev_paths:
            if os.path.exists(path):
                return path

        # Check for local build (relative to kernel location)
        kernel_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_build_path = os.path.join(kernel_dir, 'ariane-xml-c-kernel', 'build', 'ariane-xml')
        if os.path.exists(local_build_path):
            return local_build_path

        # Try common locations
        candidates = [
            '/usr/local/bin/ariane-xml',
            '/usr/bin/ariane-xml',
            'ariane-xml',  # In PATH
            os.path.expanduser('~/.local/bin/ariane-xml')
        ]

        for path in candidates:
            try:
                result = subprocess.run(
                    [path, '--version'] if path != 'ariane-xml' else ['ariane-xml', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 or 'ariane-xml' in result.stdout.lower() or 'ariane-xml' in result.stderr.lower():
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        return docker_path  # Default for Docker environment

    def _find_working_directory(self) -> str:
        """Find the appropriate working directory for query execution"""
        # If we're using a development build, use the project root
        if '/home/user/ariane-xml' in self.ariane_xml_path:
            return '/home/user/ariane-xml'

        if os.path.expanduser('~/ariane-xml') in self.ariane_xml_path:
            return os.path.expanduser('~/ariane-xml')

        # For Docker or system-installed versions, use current directory
        return os.getcwd()

    def _is_dsn_command(self, query: str) -> bool:
        """Check if the query is a DSN-specific command"""
        query_upper = query.strip().upper()
        dsn_keywords = [
            'SET MODE DSN',
            'SET MODE STANDARD',
            'SHOW MODE',
            'SET DSN_VERSION',
            'SHOW DSN_SCHEMA',
            'DESCRIBE ',
            'TEMPLATE ',
            'COMPARE P',
        ]
        return any(query_upper.startswith(kw) for kw in dsn_keywords)

    def _update_dsn_state(self, query: str):
        """Update internal DSN state based on the command"""
        query_upper = query.strip().upper()

        # Track DSN mode activation
        if 'SET MODE DSN' in query_upper:
            self.dsn_mode = True
        elif 'SET MODE STANDARD' in query_upper:
            self.dsn_mode = False
            self.dsn_version = None

        # Track DSN version
        if 'SET DSN_VERSION' in query_upper:
            if 'P25' in query_upper:
                self.dsn_version = 'P25'
            elif 'P26' in query_upper:
                self.dsn_version = 'P26'
            elif 'AUTO' in query_upper:
                self.dsn_version = 'AUTO'

    def _get_dsn_mode_badge(self) -> str:
        """Get a badge showing current DSN mode status"""
        if not self.dsn_mode:
            return ""

        version_str = f" [{self.dsn_version}]" if self.dsn_version else ""
        return f"🇫🇷 DSN MODE{version_str}"

    def _execute_query(self, query: str) -> Dict[str, Any]:
        """Execute an Ariane-XML query and return the result"""
        try:
            query = query.strip()
            # Remove trailing semicolon if present (SQL-style)
            if query.endswith(';'):
                query = query[:-1].strip()
            if not query:
                return {'success': True, 'output': '', 'error': None}

            result = subprocess.run(
                [self.ariane_xml_path, query],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.working_directory
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'output': result.stdout,
                    'error': result.stderr or f"Ariane-XML exited with code {result.returncode}"
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': '⏱️  Query execution timed out (30s limit)\n\n💡 Tip: Try adding a LIMIT clause or filtering with WHERE to reduce results.'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'output': '',
                'error': f'❌ Ariane-XML executable not found at: {self.ariane_xml_path}\n\n'
                        '📋 Please ensure Ariane-XML is built:\n'
                        '   Docker: Already built during image creation\n'
                        '   Local: cd build && cmake .. && make'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'💥 Unexpected error: {str(e)}'
            }

    def _format_dsn_describe_output(self, output: str) -> str:
        """Format DESCRIBE command output with enhanced styling"""
        lines = output.strip().split('\n')
        html = ['<div style="font-family: monospace; background: #f6f8fa; padding: 15px; border-radius: 6px; border-left: 4px solid #0366d6;">']

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Highlight field labels
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                html.append(f'<div style="margin: 4px 0;"><strong style="color: #0366d6;">{self._escape_html(label)}:</strong> {self._escape_html(value)}</div>')
            else:
                html.append(f'<div style="margin: 4px 0;">{self._escape_html(line)}</div>')

        html.append('</div>')
        return ''.join(html)

    def _format_dsn_template_list(self, output: str) -> str:
        """Format TEMPLATE LIST output with enhanced styling"""
        lines = output.strip().split('\n')
        html = ['<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif;">']
        html.append('<h3 style="color: #24292e; margin-top: 0;">📋 Available DSN Templates</h3>')
        html.append('<div style="display: grid; gap: 10px;">')

        current_category = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect category headers
            if line.endswith(':') or 'Category' in line or 'Templates' in line:
                if current_category:
                    html.append('</div>')  # Close previous category
                current_category = line
                html.append(f'<div style="margin-top: 10px;"><h4 style="color: #0366d6; margin: 5px 0;">{self._escape_html(line)}</h4>')
            elif line.startswith('-') or line.startswith('•'):
                # Template item
                template_name = line.lstrip('-•').strip()
                html.append(f'<div style="padding: 8px; background: #f6f8fa; border-radius: 4px; margin: 4px 0;">{self._escape_html(template_name)}</div>')
            else:
                html.append(f'<div style="margin: 4px 0;">{self._escape_html(line)}</div>')

        if current_category:
            html.append('</div>')  # Close last category
        html.append('</div></div>')
        return ''.join(html)

    def _format_dsn_compare_output(self, output: str) -> str:
        """Format COMPARE command output with enhanced styling"""
        lines = output.strip().split('\n')
        html = ['<div style="font-family: monospace; padding: 15px; background: #fff; border: 1px solid #e1e4e8; border-radius: 6px;">']
        html.append('<h3 style="color: #24292e; margin-top: 0;">📊 DSN Schema Comparison</h3>')

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                html.append('<br/>')
                continue

            # Color-code different types of changes
            if line_stripped.startswith('+'):
                html.append(f'<div style="color: #28a745; margin: 2px 0;">▸ {self._escape_html(line_stripped)}</div>')
            elif line_stripped.startswith('-'):
                html.append(f'<div style="color: #d73a49; margin: 2px 0;">▸ {self._escape_html(line_stripped)}</div>')
            elif line_stripped.startswith('≠') or 'Modified' in line_stripped:
                html.append(f'<div style="color: #f9826c; margin: 2px 0;">▸ {self._escape_html(line_stripped)}</div>')
            elif line_stripped.startswith('Summary') or line_stripped.startswith('Total'):
                html.append(f'<div style="font-weight: bold; color: #0366d6; margin: 8px 0;">{self._escape_html(line_stripped)}</div>')
            else:
                html.append(f'<div style="margin: 2px 0;">{self._escape_html(line_stripped)}</div>')

        html.append('</div>')
        return ''.join(html)

    def _format_output(self, output: str, is_error: bool = False, query: str = '') -> Dict[str, Any]:
        """
        Format output with rich HTML tables

        Detects table-like output and renders as styled HTML.
        Falls back to plain text for non-table output.
        """
        if not output:
            return {'text/plain': '(no output)'}

        # Preserve the plain text version
        plain_output = output

        # Enhanced formatting for DSN-specific commands
        query_upper = query.strip().upper()

        if 'DESCRIBE' in query_upper and self.dsn_mode:
            html = self._format_dsn_describe_output(output)
            return {
                'text/html': html,
                'text/plain': plain_output
            }

        if 'TEMPLATE LIST' in query_upper:
            html = self._format_dsn_template_list(output)
            return {
                'text/html': html,
                'text/plain': plain_output
            }

        if 'COMPARE' in query_upper and ('P25' in query_upper or 'P26' in query_upper):
            html = self._format_dsn_compare_output(output)
            return {
                'text/html': html,
                'text/plain': plain_output
            }

        # Try to parse as table
        lines = output.strip().split('\n')

        # Check if this looks like a table (contains | separators)
        if len(lines) > 0 and '|' in lines[0]:
            html = self._create_html_table(lines)
            return {
                'text/html': html,
                'text/plain': plain_output  # Fallback
            }

        # Not a table, return plain text
        return {'text/plain': plain_output}

    def _create_html_table(self, lines: List[str]) -> str:
        """
        Convert pipe-separated output to beautiful HTML table

        Handles:
        - Header row
        - Data rows
        - Result count footer
        - Numeric vs text alignment
        """
        html = []

        # Add CSS styling
        html.append('''
<style>
    .ariane-xml-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        margin: 15px 0;
    }
    .ariane-xml-table {
        border-collapse: collapse;
        width: 100%;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-radius: 4px;
        overflow: hidden;
    }
    .ariane-xml-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #5568d3;
    }
    .ariane-xml-table td {
        padding: 10px 16px;
        border-bottom: 1px solid #e1e4e8;
        font-size: 14px;
        color: #24292e;
    }
    .ariane-xml-table tr:last-child td {
        border-bottom: none;
    }
    .ariane-xml-table tr:hover {
        background-color: #f6f8fa;
    }
    .ariane-xml-table tr:nth-child(even) {
        background-color: #fafbfc;
    }
    .ariane-xml-table td.numeric {
        text-align: right;
        font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        color: #0366d6;
    }
    .ariane-xml-result-count {
        color: #586069;
        font-size: 13px;
        font-style: italic;
        margin-top: 8px;
        padding: 8px 12px;
        background: #f6f8fa;
        border-radius: 4px;
        display: inline-block;
    }
    .ariane-xml-result-count::before {
        content: "✓ ";
        color: #28a745;
        font-weight: bold;
    }
</style>
''')

        html.append('<div class="ariane-xml-container">')
        html.append('<table class="ariane-xml-table">')

        # Parse rows
        table_rows = []
        result_count = None

        for line in lines:
            if 'row(s) returned' in line or 'rows returned' in line:
                result_count = line.strip()
                continue

            if line.strip():
                table_rows.append(line)

        # Process table rows
        if table_rows:
            # Header row
            if len(table_rows) > 0:
                cells = [cell.strip() for cell in table_rows[0].split('|')]
                cells = [c for c in cells if c]  # Remove empty cells

                html.append('<thead><tr>')
                for cell in cells:
                    html.append(f'<th>{self._escape_html(cell)}</th>')
                html.append('</tr></thead>')

            # Data rows
            if len(table_rows) > 1:
                html.append('<tbody>')
                for line in table_rows[1:]:
                    cells = [cell.strip() for cell in line.split('|')]
                    cells = [c for c in cells if c]  # Remove empty cells

                    html.append('<tr>')
                    for cell in cells:
                        # Detect if cell contains numeric data
                        cell_class = 'numeric' if self._is_numeric(cell) else ''
                        class_attr = f' class="{cell_class}"' if cell_class else ''
                        html.append(f'<td{class_attr}>{self._escape_html(cell)}</td>')
                    html.append('</tr>')
                html.append('</tbody>')

        html.append('</table>')

        # Add result count
        if result_count:
            html.append(f'<div class="ariane-xml-result-count">{self._escape_html(result_count)}</div>')

        html.append('</div>')

        return ''.join(html)

    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        # Remove common currency symbols and whitespace
        cleaned = value.replace('$', '').replace(',', '').strip()
        try:
            float(cleaned)
            return True
        except ValueError:
            return False

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def do_execute(
        self,
        code: str,
        silent: bool,
        store_history: bool = True,
        user_expressions: Optional[Dict] = None,
        allow_stdin: bool = False
    ) -> Dict[str, Any]:
        """Execute user code (Ariane-XML query)"""
        if not code.strip():
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }

        # Update DSN state if this is a DSN command
        if self._is_dsn_command(code):
            self._update_dsn_state(code)

        # Show execution status with DSN mode badge
        if not silent:
            mode_badge = self._get_dsn_mode_badge()
            status_msg = '⚡ Executing query...'
            if mode_badge:
                status_msg = f'{mode_badge} ⚡ Executing query...'
            self.send_response(
                self.iopub_socket,
                'stream',
                {
                    'name': 'stdout',
                    'text': f'{status_msg}\n'
                }
            )

        # Execute the query and track timing
        start_time = time.time()
        result = self._execute_query(code)
        execution_time_ms = (time.time() - start_time) * 1000

        if not silent:
            if result['success']:
                # Send formatted output
                if result['output']:
                    display_data = self._format_output(result['output'], query=code)
                    self.send_response(
                        self.iopub_socket,
                        'display_data',
                        {
                            'data': display_data,
                            'metadata': {}
                        }
                    )
                    # Send completion message with timing
                    self.send_response(
                        self.iopub_socket,
                        'stream',
                        {
                            'name': 'stdout',
                            'text': f'\n✓ Done in {execution_time_ms:.1f} ms\n'
                        }
                    )
                else:
                    # Query succeeded but produced no output - provide helpful feedback
                    help_msg = f'\n✓ Query executed successfully (no output) - {execution_time_ms:.1f} ms\n\n'
                    help_msg += '💡 Possible reasons:\n'
                    help_msg += '   • File path not found\n'
                    help_msg += '   • Query syntax may be incorrect\n'
                    help_msg += '   • No data matched your WHERE clause\n'
                    help_msg += '   • Empty XML file\n\n'
                    help_msg += 'Tip: Check your file path and query syntax.'

                    # Add DSN-specific help if in DSN mode
                    if self.dsn_mode:
                        help_msg += '\n\n🇫🇷 DSN MODE Tips:\n'
                        help_msg += '   • Use "DESCRIBE <field>" to see field documentation\n'
                        help_msg += '   • Use "TEMPLATE LIST" to see available query templates\n'
                        help_msg += '   • Check DSN version with "SHOW DSN_SCHEMA"\n'

                    self.send_response(
                        self.iopub_socket,
                        'stream',
                        {
                            'name': 'stdout',
                            'text': help_msg
                        }
                    )
            else:
                # Send formatted error with timing
                error_msg = result['error'] or 'Unknown error'
                self.send_response(
                    self.iopub_socket,
                    'stream',
                    {
                        'name': 'stderr',
                        'text': f'{error_msg}\n\n✗ Failed after {execution_time_ms:.1f} ms\n'
                    }
                )

        # Return execution result
        if result['success']:
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }
        else:
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': 'Ariane-XMLError',
                'evalue': result['error'] or 'Query execution failed',
                'traceback': [result['error'] or 'Query execution failed']
            }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=ArianeXMLKernel)
