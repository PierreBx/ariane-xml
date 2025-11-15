#!/usr/bin/env python3
"""
ExpoCLI Jupyter Kernel - Enhanced Version with HTML Table Output

This is a proof-of-concept enhancement showing rich HTML table formatting.
To use: Copy this over kernel.py or import specific methods.
"""

from ipykernel.kernelbase import Kernel
import subprocess
import re
import os
from typing import Dict, Any, List, Optional


class ExpoCLIKernel(Kernel):
    """Enhanced Jupyter kernel for ExpoCLI with rich HTML output"""

    implementation = 'ExpoCLI'
    implementation_version = '1.1.0'
    language = 'expocli-sql'
    language_version = '1.0'
    language_info = {
        'name': 'expocli-sql',
        'mimetype': 'text/x-sql',
        'file_extension': '.eql',
        'codemirror_mode': 'sql',
        'pygments_lexer': 'sql'
    }
    banner = """ExpoCLI Kernel Enhanced - SQL-like XML Querying

Execute SQL-like queries on XML files with rich HTML output.

Features:
  ✨ Styled HTML tables with zebra striping
  ✨ Hover effects for better readability
  ✨ Automatic numeric/text alignment
  ✨ Responsive design

Example queries:
  SELECT name, price FROM examples/books.xml WHERE price > 30
  SELECT * FROM examples/test.xml ORDER BY price DESC

Special commands:
  help                 - Show ExpoCLI help
  SET XSD <file>       - Set XSD schema
  SHOW XSD            - Show current XSD
"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expocli_path = self._find_expocli()

    def _find_expocli(self) -> str:
        """Locate the ExpoCLI executable"""
        # In Docker, check the build directory first
        docker_path = '/app/build/expocli'
        if os.path.exists(docker_path):
            return docker_path

        # Try common locations
        candidates = [
            '/usr/local/bin/expocli',
            '/usr/bin/expocli',
            'expocli',  # In PATH
            os.path.expanduser('~/.local/bin/expocli')
        ]

        for path in candidates:
            try:
                result = subprocess.run(
                    [path, '--version'] if path != 'expocli' else ['expocli', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 or 'expocli' in result.stdout.lower() or 'expocli' in result.stderr.lower():
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        return docker_path  # Default for Docker environment

    def _execute_query(self, query: str) -> Dict[str, Any]:
        """Execute an ExpoCLI query and return the result"""
        try:
            query = query.strip()
            if not query:
                return {'success': True, 'output': '', 'error': None}

            result = subprocess.run(
                [self.expocli_path, query],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
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
                    'error': result.stderr or f"ExpoCLI exited with code {result.returncode}"
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
                'error': f'❌ ExpoCLI executable not found at: {self.expocli_path}\n\n'
                        '📋 Please ensure ExpoCLI is built:\n'
                        '   Docker: Already built during image creation\n'
                        '   Local: cd build && cmake .. && make'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'💥 Unexpected error: {str(e)}'
            }

    def _format_output(self, output: str, is_error: bool = False) -> Dict[str, Any]:
        """
        Format output with rich HTML tables

        Detects table-like output and renders as styled HTML.
        Falls back to plain text for non-table output.
        """
        if not output:
            return {'text/plain': '(no output)'}

        # Preserve the plain text version
        plain_output = output

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
    .expocli-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        margin: 15px 0;
    }
    .expocli-table {
        border-collapse: collapse;
        width: 100%;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-radius: 4px;
        overflow: hidden;
    }
    .expocli-table th {
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
    .expocli-table td {
        padding: 10px 16px;
        border-bottom: 1px solid #e1e4e8;
        font-size: 14px;
        color: #24292e;
    }
    .expocli-table tr:last-child td {
        border-bottom: none;
    }
    .expocli-table tr:hover {
        background-color: #f6f8fa;
    }
    .expocli-table tr:nth-child(even) {
        background-color: #fafbfc;
    }
    .expocli-table td.numeric {
        text-align: right;
        font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        color: #0366d6;
    }
    .expocli-result-count {
        color: #586069;
        font-size: 13px;
        font-style: italic;
        margin-top: 8px;
        padding: 8px 12px;
        background: #f6f8fa;
        border-radius: 4px;
        display: inline-block;
    }
    .expocli-result-count::before {
        content: "✓ ";
        color: #28a745;
        font-weight: bold;
    }
</style>
''')

        html.append('<div class="expocli-container">')
        html.append('<table class="expocli-table">')

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
            html.append(f'<div class="expocli-result-count">{self._escape_html(result_count)}</div>')

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
        """Execute user code (ExpoCLI query)"""
        if not code.strip():
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }

        # Execute the query
        result = self._execute_query(code)

        if not silent:
            if result['success']:
                # Send formatted output
                if result['output']:
                    display_data = self._format_output(result['output'])
                    self.send_response(
                        self.iopub_socket,
                        'display_data',
                        {
                            'data': display_data,
                            'metadata': {}
                        }
                    )
            else:
                # Send formatted error
                error_msg = result['error'] or 'Unknown error'
                self.send_response(
                    self.iopub_socket,
                    'stream',
                    {
                        'name': 'stderr',
                        'text': error_msg
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
                'ename': 'ExpoCLIError',
                'evalue': result['error'] or 'Query execution failed',
                'traceback': [result['error'] or 'Query execution failed']
            }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=ExpoCLIKernel)
