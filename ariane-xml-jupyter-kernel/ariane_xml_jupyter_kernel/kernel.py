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
import json
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
        self.dsn_quickstart = True  # Show quick reference card on DSN mode activation

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
            'SET DSN_QUICKSTART',
            'SHOW DSN_SCHEMA',
            'DESCRIBE ',
            'TEMPLATE ',
            'COMPARE P',
            'HELP',
            '?',
            'BROWSE ',
            'SEARCH ',
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

        # Track quickstart display preference
        if 'SET DSN_QUICKSTART' in query_upper:
            if 'OFF' in query_upper:
                self.dsn_quickstart = False
            elif 'ON' in query_upper:
                self.dsn_quickstart = True

    def _get_dsn_mode_badge(self) -> str:
        """Get a badge showing current DSN mode status"""
        if not self.dsn_mode:
            return ""

        version_str = f" [{self.dsn_version}]" if self.dsn_version else ""
        return f"🇫🇷 DSN MODE{version_str}"

    def _get_dsn_quickstart_card(self) -> str:
        """Generate Quick Reference Card HTML for DSN mode"""
        version_str = f" [Version: {self.dsn_version}]" if self.dsn_version else ""

        html = f'''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background: linear-gradient(135deg, #f6f8fc 0%, #ffffff 100%);
            box-shadow: 0 4px 6px rgba(102, 126, 234, 0.15);">

    <h2 style="margin: 0 0 20px 0;
               color: #667eea;
               border-bottom: 2px solid #667eea;
               padding-bottom: 10px;
               font-size: 24px;">
        🇫🇷 DSN MODE ACTIVATED{version_str}
    </h2>

    <div style="display: grid; gap: 15px;">
        <div>
            <h3 style="color: #24292e; margin: 0 0 10px 0; font-size: 16px;">📚 Quick Start Commands:</h3>
            <div style="background: white;
                       padding: 15px;
                       border-radius: 6px;
                       border-left: 4px solid #667eea;
                       font-family: 'Monaco', 'Menlo', monospace;
                       font-size: 13px;">
                <div style="margin: 6px 0;"><code style="color: #0366d6;">HELP</code> - Show detailed help</div>
                <div style="margin: 6px 0;"><code style="color: #0366d6;">BROWSE SCHEMA</code> - Explore all fields</div>
                <div style="margin: 6px 0;"><code style="color: #0366d6;">TEMPLATE LIST</code> - View query templates</div>
                <div style="margin: 6px 0;"><code style="color: #0366d6;">DESCRIBE 01_001</code> - Get field documentation</div>
                <div style="margin: 6px 0;"><code style="color: #0366d6;">SEARCH "keyword"</code> - Search fields by description</div>
            </div>
        </div>

        <div>
            <h3 style="color: #24292e; margin: 0 0 10px 0; font-size: 16px;">💡 Tips:</h3>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                <li>Press <strong>TAB</strong> for autocomplete</li>
                <li>Use shortcut notation: <code style="background: #f6f8fa; padding: 2px 6px; border-radius: 3px;">SELECT 01_001, 30_001</code></li>
                <li>Type <code style="background: #f6f8fa; padding: 2px 6px; border-radius: 3px;">HELP &lt;command&gt;</code> for specific help</li>
                <li>Use <code style="background: #f6f8fa; padding: 2px 6px; border-radius: 3px;">?</code> followed by field code for quick lookup</li>
            </ul>
        </div>

        <div style="background: #fffbeb;
                   padding: 12px;
                   border-radius: 6px;
                   border-left: 4px solid #f59e0b;
                   font-size: 13px;">
            <strong style="color: #92400e;">📖 Documentation:</strong>
            <span style="color: #451a03;">JUPYTER_DSN_INTEGRATION.md</span>
        </div>

        <div style="font-size: 12px;
                   color: #6b7280;
                   font-style: italic;
                   text-align: center;
                   margin-top: 5px;">
            To hide this message: <code style="background: #f6f8fa; padding: 2px 6px; border-radius: 3px;">SET DSN_QUICKSTART OFF</code>
        </div>
    </div>
</div>
'''
        return html

    def _handle_kernel_command(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Handle kernel-level commands that don't need C++ backend.
        Returns result dict if handled, None if should be passed to C++ backend.
        """
        query_upper = query.strip().upper()

        # HELP command
        if query_upper == 'HELP' or query_upper == 'HELP DSN':
            return self._get_help_output()

        # HELP <specific command>
        if query_upper.startswith('HELP '):
            command = query[5:].strip()
            return self._get_help_output(command)

        # Quick field lookup: ? 01_001
        if query_upper.startswith('?'):
            field_code = query[1:].strip()
            if field_code:
                # Convert to DESCRIBE command
                return None  # Let C++ handle DESCRIBE

        # BROWSE commands
        if query_upper.startswith('BROWSE'):
            return self._handle_browse_command(query)

        # SEARCH command
        if query_upper.startswith('SEARCH'):
            return self._handle_search_command(query)

        return None  # Not a kernel command, pass to C++ backend

    def _get_help_output(self, command: Optional[str] = None) -> Dict[str, Any]:
        """Generate help documentation"""
        if command:
            # Specific command help
            help_text = self._get_command_help(command.upper())
        else:
            # General help
            help_text = self._get_general_help()

        return {
            'success': True,
            'output': help_text,
            'error': None,
            'is_html': True
        }

    def _get_general_help(self) -> str:
        """Generate general DSN MODE help"""
        html = '''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 20px 0;">

    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
        🇫🇷 DSN MODE - Command Reference
    </h2>

    <div style="display: grid; gap: 20px; margin-top: 20px;">

        <!-- Mode Control -->
        <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea;">
            <h3 style="color: #24292e; margin-top: 0;">⚙️ Mode Control</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6; width: 40%;">SET MODE DSN</td>
                    <td style="padding: 8px;">Activate DSN mode</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">SET MODE STANDARD</td>
                    <td style="padding: 8px;">Deactivate DSN mode</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">SET DSN_VERSION P25</td>
                    <td style="padding: 8px;">Use P25 schema</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">SET DSN_VERSION P26</td>
                    <td style="padding: 8px;">Use P26 schema</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">SHOW MODE</td>
                    <td style="padding: 8px;">Display current mode</td>
                </tr>
            </table>
        </div>

        <!-- Discovery Commands -->
        <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
            <h3 style="color: #24292e; margin-top: 0;">🔍 Discovery & Exploration</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6; width: 40%;">BROWSE SCHEMA</td>
                    <td style="padding: 8px;">Explore all available fields</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">BROWSE BLOC 01</td>
                    <td style="padding: 8px;">Show all fields in specific bloc</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">DESCRIBE 01_001</td>
                    <td style="padding: 8px;">Show field documentation</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">SEARCH "keyword"</td>
                    <td style="padding: 8px;">Search fields by description</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">? 01_001</td>
                    <td style="padding: 8px;">Quick field lookup (same as DESCRIBE)</td>
                </tr>
            </table>
        </div>

        <!-- Query Commands -->
        <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b;">
            <h3 style="color: #24292e; margin-top: 0;">📊 Query Operations</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6; width: 40%;">SELECT 01_001, 30_001 FROM file.xml</td>
                    <td style="padding: 8px;">Query with shortcut notation</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">WHERE, ORDER BY, LIMIT</td>
                    <td style="padding: 8px;">Standard SQL operations</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">TEMPLATE LIST</td>
                    <td style="padding: 8px;">View available query templates</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">TEMPLATE &lt;name&gt;</td>
                    <td style="padding: 8px;">Use a predefined template</td>
                </tr>
            </table>
        </div>

        <!-- Schema Tools -->
        <div style="background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #d73a49;">
            <h3 style="color: #24292e; margin-top: 0;">🔄 Schema Tools</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-family: monospace; color: #0366d6; width: 40%;">SHOW DSN_SCHEMA</td>
                    <td style="padding: 8px;">Display schema information</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-family: monospace; color: #0366d6;">COMPARE P25 P26</td>
                    <td style="padding: 8px;">Compare schema versions</td>
                </tr>
            </table>
        </div>

        <!-- Help -->
        <div style="background: #f6f8fa; padding: 15px; border-radius: 6px;">
            <h3 style="color: #24292e; margin-top: 0;">💡 Getting More Help</h3>
            <p style="margin: 5px 0;">• Type <code style="background: white; padding: 2px 6px; border-radius: 3px;">HELP &lt;command&gt;</code> for detailed help on a specific command</p>
            <p style="margin: 5px 0;">• Press <strong>TAB</strong> for autocomplete suggestions</p>
            <p style="margin: 5px 0;">• See <code>JUPYTER_DSN_INTEGRATION.md</code> for full documentation</p>
        </div>
    </div>
</div>
'''
        return html

    def _get_command_help(self, command: str) -> str:
        """Get help for a specific command"""
        help_db = {
            'BROWSE': {
                'title': 'BROWSE - Schema Explorer',
                'usage': [
                    'BROWSE SCHEMA',
                    'BROWSE BLOC 01',
                    'BROWSE BLOC 30'
                ],
                'description': 'Explore DSN schema fields interactively.',
                'examples': [
                    ('BROWSE SCHEMA', 'Show all available fields organized by bloc'),
                    ('BROWSE BLOC 01', 'Show all fields in bloc 01 (Identification)')
                ]
            },
            'DESCRIBE': {
                'title': 'DESCRIBE - Field Documentation',
                'usage': [
                    'DESCRIBE <field_code>',
                    '? <field_code>'
                ],
                'description': 'Display detailed documentation for a specific field.',
                'examples': [
                    ('DESCRIBE 01_001', 'Show documentation for field 01_001'),
                    ('? 30_001', 'Quick lookup for NIR field')
                ]
            },
            'SEARCH': {
                'title': 'SEARCH - Find Fields',
                'usage': [
                    'SEARCH "keyword"',
                    'SEARCH "text with spaces"'
                ],
                'description': 'Search for fields by description or name.',
                'examples': [
                    ('SEARCH "numéro"', 'Find all fields containing "numéro"'),
                    ('SEARCH "naissance"', 'Find birth-related fields')
                ]
            },
            'TEMPLATE': {
                'title': 'TEMPLATE - Query Templates',
                'usage': [
                    'TEMPLATE LIST',
                    'TEMPLATE <name>'
                ],
                'description': 'Use predefined query templates for common operations.',
                'examples': [
                    ('TEMPLATE LIST', 'Show all available templates'),
                    ('TEMPLATE demographics', 'Use the demographics template')
                ]
            },
            'COMPARE': {
                'title': 'COMPARE - Schema Comparison',
                'usage': [
                    'COMPARE P25 P26'
                ],
                'description': 'Compare differences between DSN schema versions.',
                'examples': [
                    ('COMPARE P25 P26', 'Show differences between P25 and P26')
                ]
            }
        }

        # Find matching command
        for key in help_db:
            if command.startswith(key):
                info = help_db[key]
                html = f'''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 20px 0;">

    <h2 style="color: #667eea; margin-top: 0;">{info['title']}</h2>

    <div style="margin: 15px 0;">
        <h3 style="color: #24292e;">Usage:</h3>
        <div style="background: #f6f8fa; padding: 15px; border-radius: 4px; font-family: monospace;">
'''
                for usage in info['usage']:
                    html += f'            <div style="margin: 5px 0; color: #0366d6;">{self._escape_html(usage)}</div>\n'

                html += f'''        </div>
    </div>

    <div style="margin: 15px 0;">
        <h3 style="color: #24292e;">Description:</h3>
        <p>{info['description']}</p>
    </div>

    <div style="margin: 15px 0;">
        <h3 style="color: #24292e;">Examples:</h3>
'''
                for example, desc in info['examples']:
                    html += f'''        <div style="margin: 10px 0; padding: 10px; background: #f6f8fa; border-radius: 4px;">
            <code style="color: #0366d6; display: block; margin-bottom: 5px;">{self._escape_html(example)}</code>
            <span style="color: #586069; font-size: 13px;">{desc}</span>
        </div>
'''
                html += '''    </div>
</div>
'''
                return html

        # Command not found
        return f'''
<div style="padding: 20px; background: #fff3cd; border-left: 4px solid #f59e0b; border-radius: 4px;">
    <strong>⚠️ Unknown command: {self._escape_html(command)}</strong>
    <p>Type <code>HELP</code> to see all available commands.</p>
</div>
'''

    def _handle_browse_command(self, query: str) -> Dict[str, Any]:
        """Handle BROWSE commands (implemented in kernel for better UX)"""
        query_upper = query.strip().upper()

        # Parse BROWSE command
        if query_upper == 'BROWSE SCHEMA':
            return self._get_browse_schema_output()
        elif 'BROWSE BLOC' in query_upper:
            # Extract bloc number
            parts = query.strip().split()
            if len(parts) >= 3:
                bloc_num = parts[2]
                return self._get_browse_bloc_output(bloc_num)
            else:
                return {
                    'success': False,
                    'output': '',
                    'error': 'Usage: BROWSE BLOC <number>\nExample: BROWSE BLOC 01',
                    'is_html': False
                }

        # Unknown BROWSE command
        return {
            'success': False,
            'output': '',
            'error': 'Usage: BROWSE SCHEMA or BROWSE BLOC <number>',
            'is_html': False
        }

    def _get_browse_schema_output(self) -> Dict[str, Any]:
        """Generate schema browser output"""
        if not self.dsn_version:
            return {
                'success': False,
                'output': '',
                'error': 'Please set DSN version first: SET DSN_VERSION P26',
                'is_html': False
            }

        html = f'''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 1000px;
            margin: 20px 0;">

    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
        📚 DSN Schema Browser - {self.dsn_version}
    </h2>

    <div style="background: #f6f8fa; padding: 15px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; color: #586069;">
            <strong>Quick Navigation:</strong> Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">BROWSE BLOC &lt;number&gt;</code> to explore a specific bloc
        </p>
    </div>

    <div style="display: grid; gap: 15px; margin-top: 20px;">

        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #24292e; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">01️⃣</span>
                Bloc 01 - Identification
            </h3>
            <p style="color: #586069; margin: 10px 0;">Main identification fields</p>
            <div style="font-family: monospace; font-size: 13px; color: #0366d6;">
                <div>• 01_001 - Numéro d'inscription au RPPS</div>
                <div>• 01_002 - Clé du numéro</div>
                <div>• 01_003 - Numéro ADELI</div>
            </div>
            <button style="margin-top: 10px; padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;"
                    onclick="navigator.clipboard.writeText('BROWSE BLOC 01')">
                📋 Explore Bloc 01
            </button>
        </div>

        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #24292e; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">02️⃣</span>
                Bloc 02 - Naissance
            </h3>
            <p style="color: #586069; margin: 10px 0;">Birth information fields</p>
            <div style="font-family: monospace; font-size: 13px; color: #28a745;">
                <div>• 02_001 - Date de naissance</div>
                <div>• 02_002 - Lieu de naissance</div>
                <div>• 02_003 - Code commune</div>
            </div>
            <button style="margin-top: 10px; padding: 6px 12px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;"
                    onclick="navigator.clipboard.writeText('BROWSE BLOC 02')">
                📋 Explore Bloc 02
            </button>
        </div>

        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #24292e; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">30️⃣</span>
                Bloc 30 - NIR (Numéro d'Inscription au Répertoire)
            </h3>
            <p style="color: #586069; margin: 10px 0;">Social security number fields</p>
            <div style="font-family: monospace; font-size: 13px; color: #f59e0b;">
                <div>• 30_001 - NIR</div>
                <div>• 30_002 - Clé NIR</div>
            </div>
            <button style="margin-top: 10px; padding: 6px 12px; background: #f59e0b; color: white; border: none; border-radius: 4px; cursor: pointer;"
                    onclick="navigator.clipboard.writeText('BROWSE BLOC 30')">
                📋 Explore Bloc 30
            </button>
        </div>

        <div style="background: #fffbeb; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b;">
            <strong style="color: #92400e;">💡 Pro Tips:</strong>
            <ul style="margin: 10px 0; padding-left: 20px; color: #92400e;">
                <li>Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">DESCRIBE &lt;field&gt;</code> for detailed field documentation</li>
                <li>Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">SEARCH "keyword"</code> to find fields by description</li>
                <li>Press <strong>TAB</strong> while typing field codes for autocomplete</li>
            </ul>
        </div>

    </div>
</div>
'''
        return {
            'success': True,
            'output': html,
            'error': None,
            'is_html': True
        }

    def _get_browse_bloc_output(self, bloc_num: str) -> Dict[str, Any]:
        """Generate bloc-specific browser output"""
        if not self.dsn_version:
            return {
                'success': False,
                'output': '',
                'error': 'Please set DSN version first: SET DSN_VERSION P26',
                'is_html': False
            }

        # Sample data for common blocs (in real implementation, this would come from schema)
        bloc_data = {
            '01': {
                'name': 'Identification',
                'fields': [
                    ('01_001', 'Numéro d\'inscription au RPPS', 'VARCHAR(11)'),
                    ('01_002', 'Clé du numéro RPPS', 'CHAR(1)'),
                    ('01_003', 'Numéro ADELI', 'VARCHAR(9)'),
                    ('01_004', 'Civilité', 'CHAR(3)'),
                    ('01_005', 'Nom de famille', 'VARCHAR(80)'),
                    ('01_006', 'Prénom', 'VARCHAR(60)'),
                ]
            },
            '02': {
                'name': 'Naissance',
                'fields': [
                    ('02_001', 'Date de naissance', 'DATE'),
                    ('02_002', 'Lieu de naissance', 'VARCHAR(80)'),
                    ('02_003', 'Code commune de naissance', 'CHAR(5)'),
                    ('02_004', 'Code pays de naissance', 'CHAR(5)'),
                ]
            },
            '30': {
                'name': 'NIR',
                'fields': [
                    ('30_001', 'Numéro d\'inscription au répertoire (NIR)', 'CHAR(13)'),
                    ('30_002', 'Clé NIR', 'CHAR(2)'),
                ]
            }
        }

        if bloc_num not in bloc_data:
            html = f'''
<div style="background: #fff3cd; padding: 20px; border-left: 4px solid #f59e0b; border-radius: 4px;">
    <strong>⚠️ Bloc {self._escape_html(bloc_num)} information not available</strong>
    <p>Use <code>BROWSE SCHEMA</code> to see all available blocs.</p>
    <p>Common blocs: 01 (Identification), 02 (Naissance), 30 (NIR)</p>
</div>
'''
            return {
                'success': True,
                'output': html,
                'error': None,
                'is_html': True
            }

        bloc_info = bloc_data[bloc_num]
        html = f'''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 20px 0;">

    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
        📂 Bloc {self._escape_html(bloc_num)} - {self._escape_html(bloc_info['name'])}
    </h2>

    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f6f8fa; border-bottom: 2px solid #e1e4e8;">
                    <th style="padding: 12px; text-align: left; color: #24292e;">Field Code</th>
                    <th style="padding: 12px; text-align: left; color: #24292e;">Description</th>
                    <th style="padding: 12px; text-align: left; color: #24292e;">Type</th>
                </tr>
            </thead>
            <tbody>
'''
        for code, desc, type_info in bloc_info['fields']:
            html += f'''
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 12px; font-family: monospace; color: #0366d6; font-weight: 600;">{self._escape_html(code)}</td>
                    <td style="padding: 12px; color: #24292e;">{self._escape_html(desc)}</td>
                    <td style="padding: 12px; font-family: monospace; color: #6a737d; font-size: 12px;">{self._escape_html(type_info)}</td>
                </tr>
'''
        html += '''
            </tbody>
        </table>
    </div>

    <div style="background: #f0f9ff; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-top: 20px;">
        <strong style="color: #1e3a8a;">💡 Next Steps:</strong>
        <ul style="margin: 10px 0; padding-left: 20px; color: #1e3a8a;">
            <li>Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">DESCRIBE &lt;field_code&gt;</code> for detailed information</li>
            <li>Try a query: <code style="background: white; padding: 2px 6px; border-radius: 3px;">SELECT ''' + bloc_num + '''_001 FROM ./file.xml</code></li>
            <li>Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">BROWSE SCHEMA</code> to see all blocs</li>
        </ul>
    </div>
</div>
'''
        return {
            'success': True,
            'output': html,
            'error': None,
            'is_html': True
        }

    def _handle_search_command(self, query: str) -> Dict[str, Any]:
        """Handle SEARCH commands"""
        # Extract search keyword
        parts = query.strip().split('"')
        if len(parts) < 2:
            # Try with single quotes
            parts = query.strip().split("'")

        if len(parts) < 2:
            return {
                'success': False,
                'output': '',
                'error': 'Usage: SEARCH "keyword"\nExample: SEARCH "numéro"',
                'is_html': False
            }

        keyword = parts[1].lower()
        return self._get_search_output(keyword)

    def _get_search_output(self, keyword: str) -> Dict[str, Any]:
        """Generate search results output"""
        if not self.dsn_version:
            return {
                'success': False,
                'output': '',
                'error': 'Please set DSN version first: SET DSN_VERSION P26',
                'is_html': False
            }

        # Sample searchable fields (in real implementation, search all schema fields)
        all_fields = [
            ('01_001', 'Numéro d\'inscription au RPPS', '01'),
            ('01_002', 'Clé du numéro RPPS', '01'),
            ('01_003', 'Numéro ADELI', '01'),
            ('01_005', 'Nom de famille', '01'),
            ('01_006', 'Prénom', '01'),
            ('02_001', 'Date de naissance', '02'),
            ('02_002', 'Lieu de naissance', '02'),
            ('02_003', 'Code commune de naissance', '02'),
            ('30_001', 'Numéro d\'inscription au répertoire (NIR)', '30'),
            ('30_002', 'Clé NIR', '30'),
        ]

        # Search for keyword in field codes and descriptions
        results = [
            (code, desc, bloc)
            for code, desc, bloc in all_fields
            if keyword in code.lower() or keyword in desc.lower()
        ]

        if not results:
            html = f'''
<div style="background: #fff3cd; padding: 20px; border-left: 4px solid #f59e0b; border-radius: 4px;">
    <strong>🔍 No results found for "{self._escape_html(keyword)}"</strong>
    <p>Try:</p>
    <ul style="margin: 10px 0; padding-left: 20px;">
        <li>Using different keywords</li>
        <li>Browsing all fields with <code>BROWSE SCHEMA</code></li>
        <li>Exploring specific blocs with <code>BROWSE BLOC 01</code></li>
    </ul>
</div>
'''
            return {
                'success': True,
                'output': html,
                'error': None,
                'is_html': True
            }

        html = f'''
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 20px 0;">

    <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
        🔍 Search Results for "{self._escape_html(keyword)}"
    </h2>

    <div style="background: #f6f8fa; padding: 12px; border-radius: 4px; margin: 15px 0;">
        <strong>Found {len(results)} field(s)</strong>
    </div>

    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f6f8fa; border-bottom: 2px solid #e1e4e8;">
                    <th style="padding: 12px; text-align: left; color: #24292e;">Field Code</th>
                    <th style="padding: 12px; text-align: left; color: #24292e;">Description</th>
                    <th style="padding: 12px; text-align: left; color: #24292e;">Bloc</th>
                </tr>
            </thead>
            <tbody>
'''
        for code, desc, bloc in results:
            # Highlight the keyword in the description
            highlighted_desc = desc.replace(
                keyword,
                f'<mark style="background: #fef3c7; padding: 2px 4px; border-radius: 2px;">{keyword}</mark>'
            )
            highlighted_code = code.replace(
                keyword.upper(),
                f'<mark style="background: #fef3c7; padding: 2px 4px; border-radius: 2px;">{keyword.upper()}</mark>'
            )
            html += f'''
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 12px; font-family: monospace; color: #0366d6; font-weight: 600;">{highlighted_code}</td>
                    <td style="padding: 12px; color: #24292e;">{highlighted_desc}</td>
                    <td style="padding: 12px; font-family: monospace; color: #6a737d; font-size: 12px;">Bloc {self._escape_html(bloc)}</td>
                </tr>
'''
        html += '''
            </tbody>
        </table>
    </div>

    <div style="background: #f0f9ff; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-top: 20px;">
        <strong style="color: #1e3a8a;">💡 Next Steps:</strong>
        <ul style="margin: 10px 0; padding-left: 20px; color: #1e3a8a;">
            <li>Use <code style="background: white; padding: 2px 6px; border-radius: 3px;">DESCRIBE &lt;field_code&gt;</code> for detailed field information</li>
            <li>Refine your search with different keywords</li>
        </ul>
    </div>
</div>
'''
        return {
            'success': True,
            'output': html,
            'error': None,
            'is_html': True
        }

    def _enhance_error_message(self, error_msg: str, query: str) -> str:
        """
        Enhance error messages with helpful suggestions and tips.
        Analyzes the error and provides context-aware guidance.
        """
        if not error_msg:
            return error_msg

        # Build enhanced HTML error message
        html = '<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif;">'

        # Main error display
        html += '''
<div style="background: #fff5f5;
            border-left: 4px solid #f56565;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 24px;">❌</span>
        <strong style="color: #c53030; font-size: 16px;">Error</strong>
    </div>
    <div style="font-family: monospace; color: #742a2a; white-space: pre-wrap;">'''
        html += self._escape_html(error_msg)
        html += '</div></div>'

        # Analyze error and provide suggestions
        suggestions = []
        tips = []

        error_lower = error_msg.lower()

        # File not found errors
        if 'no such file' in error_lower or 'cannot open' in error_lower or 'file not found' in error_lower:
            suggestions.append('Check that the file path is correct')
            suggestions.append('Use absolute paths or paths relative to the notebook directory')
            tips.append('List files with a shell command to verify paths')
            tips.append('Make sure the file has .xml extension')

        # Unknown field errors
        elif 'unknown field' in error_lower or 'invalid field' in error_lower:
            suggestions.append('Use <code>BROWSE SCHEMA</code> to see all available fields')
            suggestions.append('Use <code>SEARCH "keyword"</code> to find fields by description')
            suggestions.append('Verify you\'re using the correct DSN version (P25 or P26)')
            tips.append('Field codes are case-sensitive')
            tips.append('Use TAB for autocomplete when typing field names')

        # Syntax errors
        elif 'syntax' in error_lower or 'parse' in error_lower:
            suggestions.append('Check your SQL syntax')
            suggestions.append('Make sure field names are separated by commas')
            suggestions.append('Verify you have a FROM clause with a file path')
            tips.append('Type <code>HELP</code> to see command syntax')
            tips.append('Use <code>TEMPLATE LIST</code> to see example queries')

        # DSN mode not activated
        elif 'dsn' in error_lower and 'not' in error_lower:
            suggestions.append('Activate DSN mode with: <code>SET MODE DSN</code>')
            suggestions.append('Set DSN version with: <code>SET DSN_VERSION P26</code>')

        # Schema/version errors
        elif 'schema' in error_lower or 'version' in error_lower:
            suggestions.append('Set DSN version: <code>SET DSN_VERSION P25</code> or <code>SET DSN_VERSION P26</code>')
            suggestions.append('Use <code>SHOW DSN_SCHEMA</code> to see current schema info')
            suggestions.append('Compare versions with: <code>COMPARE P25 P26</code>')

        # Empty result isn't really an error, but let's handle it
        elif 'no rows' in error_lower or 'empty' in error_lower:
            suggestions.append('Check your WHERE clause filters')
            suggestions.append('Verify the XML file contains data')
            tips.append('Remove the WHERE clause to see all data')

        # Add suggestions section if we have any
        if suggestions:
            html += '''
<div style="background: #fffaf0;
            border-left: 4px solid #ed8936;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 20px;">💡</span>
        <strong style="color: #7c2d12; font-size: 15px;">Suggestions</strong>
    </div>
    <ul style="margin: 5px 0; padding-left: 25px; color: #7c2d12;">'''
            for suggestion in suggestions:
                html += f'<li style="margin: 5px 0;">{suggestion}</li>'
            html += '</ul></div>'

        # Add tips section if we have any
        if tips:
            html += '''
<div style="background: #f0f9ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 20px;">ℹ️</span>
        <strong style="color: #1e3a8a; font-size: 15px;">Tips</strong>
    </div>
    <ul style="margin: 5px 0; padding-left: 25px; color: #1e3a8a;">'''
            for tip in tips:
                html += f'<li style="margin: 5px 0;">{tip}</li>'
            html += '</ul></div>'

        # Always add help reference
        if self.dsn_mode:
            html += '''
<div style="background: #f6f8fa;
            padding: 12px;
            border-radius: 4px;
            margin: 15px 0;
            text-align: center;
            color: #586069;
            font-size: 13px;">
    Type <code style="background: white; padding: 2px 6px; border-radius: 3px; color: #0366d6;">HELP</code>
    for command reference or
    <code style="background: white; padding: 2px 6px; border-radius: 3px; color: #0366d6;">BROWSE SCHEMA</code>
    to explore available fields
</div>'''

        html += '</div>'
        return html

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

        # Track previous DSN mode state to detect activation
        was_dsn_mode = self.dsn_mode

        # Update DSN state if this is a DSN command
        if self._is_dsn_command(code):
            self._update_dsn_state(code)

        # Show DSN quickstart card when DSN mode is first activated
        show_quickstart = (not was_dsn_mode and self.dsn_mode and self.dsn_quickstart)

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

        # Check if this is a kernel-level command (like HELP)
        start_time = time.time()
        result = self._handle_kernel_command(code)

        # If not handled by kernel, execute via C++ backend
        if result is None:
            result = self._execute_query(code)

        execution_time_ms = (time.time() - start_time) * 1000

        if not silent:
            if result['success']:
                # Send formatted output
                if result['output']:
                    # Check if output is already HTML (from kernel commands)
                    if result.get('is_html', False):
                        display_data = {
                            'text/html': result['output'],
                            'text/plain': result['output']
                        }
                    else:
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

                    # Show quickstart card after DSN mode activation
                    if show_quickstart:
                        quickstart_html = self._get_dsn_quickstart_card()
                        self.send_response(
                            self.iopub_socket,
                            'display_data',
                            {
                                'data': {
                                    'text/html': quickstart_html,
                                    'text/plain': 'DSN MODE ACTIVATED - Type HELP for assistance'
                                },
                                'metadata': {}
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
                # Send enhanced formatted error
                error_msg = result['error'] or 'Unknown error'

                # Use enhanced HTML error formatting in DSN mode
                if self.dsn_mode:
                    enhanced_html = self._enhance_error_message(error_msg, code)
                    self.send_response(
                        self.iopub_socket,
                        'display_data',
                        {
                            'data': {
                                'text/html': enhanced_html,
                                'text/plain': error_msg
                            },
                            'metadata': {}
                        }
                    )
                    # Send timing info separately
                    self.send_response(
                        self.iopub_socket,
                        'stream',
                        {
                            'name': 'stderr',
                            'text': f'✗ Failed after {execution_time_ms:.1f} ms\n'
                        }
                    )
                else:
                    # Standard error output for non-DSN mode
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

    def _get_partial_word(self, code: str, cursor_pos: int) -> str:
        """
        Extract the partial word being completed at cursor position.

        For DSN mode, we want to capture field names/shortcuts being typed,
        which can contain uppercase letters, numbers, and underscores.

        Args:
            code: The current cell content
            cursor_pos: Character position of cursor

        Returns:
            The partial word at cursor position
        """
        if cursor_pos <= 0 or cursor_pos > len(code):
            return ''

        # Characters that are part of DSN field names: A-Z, 0-9, _
        # Also include lowercase for case-insensitive matching
        word_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'

        start = cursor_pos
        while start > 0 and code[start - 1] in word_chars:
            start -= 1

        return code[start:cursor_pos]

    def do_complete(self, code: str, cursor_pos: int) -> Dict[str, Any]:
        """
        Handle code completion requests from Jupyter.

        This implements the Jupyter kernel complete_request protocol,
        providing autocomplete suggestions for DSN fields, blocs, and keywords.

        Args:
            code: The current cell content
            cursor_pos: Character position of cursor in the code

        Returns:
            Dictionary with completion matches and metadata

        Jupyter Protocol Reference:
            https://jupyter-client.readthedocs.io/en/stable/messaging.html#completion
        """
        # Only provide completions in DSN mode
        if not self.dsn_mode:
            return {
                'matches': [],
                'cursor_start': cursor_pos,
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok'
            }

        try:
            # Build command for C++ autocomplete
            cmd = [
                self.ariane_xml_path,
                '--autocomplete',
                code,
                str(cursor_pos)
            ]

            # Add version parameter if DSN version is set
            if self.dsn_version:
                cmd.extend(['--version', self.dsn_version])

            # Call C++ autocomplete via subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2,  # Quick timeout for responsiveness
                cwd=self.working_directory
            )

            if result.returncode != 0:
                # Autocomplete failed, return empty
                # Log error for debugging (visible in Jupyter logs)
                if result.stderr:
                    print(f"Autocomplete error: {result.stderr}", file=__import__('sys').stderr)
                return {
                    'matches': [],
                    'cursor_start': cursor_pos,
                    'cursor_end': cursor_pos,
                    'metadata': {},
                    'status': 'ok'
                }

            # Parse JSON response from C++
            suggestions = json.loads(result.stdout)

            # Extract completion strings
            matches = [s['completion'] for s in suggestions]

            # Build metadata for rich completion UI (experimental Jupyter feature)
            # This provides type information for better UI rendering
            metadata = {
                '_jupyter_types_experimental': [
                    {
                        'text': s['completion'],
                        'type': s['type'],  # 'field', 'bloc', or 'keyword'
                        'start': cursor_pos - len(self._get_partial_word(code, cursor_pos)),
                        'end': cursor_pos
                    }
                    for s in suggestions
                ]
            }

            # Calculate completion region (the word being completed)
            partial = self._get_partial_word(code, cursor_pos)
            cursor_start = cursor_pos - len(partial)
            cursor_end = cursor_pos

            return {
                'matches': matches,
                'cursor_start': cursor_start,
                'cursor_end': cursor_end,
                'metadata': metadata,
                'status': 'ok'
            }

        except subprocess.TimeoutExpired:
            # Timeout - return empty completions
            return {
                'matches': [],
                'cursor_start': cursor_pos,
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok'
            }
        except json.JSONDecodeError as e:
            # JSON parsing error - log and return empty
            print(f"Autocomplete JSON error: {e}\nOutput: {result.stdout}", file=__import__('sys').stderr)
            return {
                'matches': [],
                'cursor_start': cursor_pos,
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok'
            }
        except Exception as e:
            # Unexpected error - log and return empty
            print(f"Autocomplete unexpected error: {e}", file=__import__('sys').stderr)
            return {
                'matches': [],
                'cursor_start': cursor_pos,
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok'
            }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=ArianeXMLKernel)
