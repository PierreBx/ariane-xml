# Jupyter Kernel User Experience Enhancements

This document outlines practical enhancements to improve the ExpoCLI Jupyter kernel user experience, prioritized by impact and implementation complexity.

## Current State (POC)

The current kernel provides basic functionality:
- ✅ Execute ExpoCLI queries in cells
- ✅ Display plain text output
- ✅ Basic error handling
- ✅ All ExpoCLI query syntax supported

## Enhancement Roadmap

### 🟢 Priority 1: High Impact, Easy to Implement

#### 1.1 Rich HTML Table Output

**Current:** Plain text output
**Enhancement:** Styled HTML tables with sortable columns

**Implementation in `kernel.py:_format_output()`:**

```python
def _format_output(self, output: str, is_error: bool = False) -> Dict[str, Any]:
    """Format output as rich HTML tables"""

    # Parse the table output
    lines = output.strip().split('\n')
    if not lines:
        return {'text/plain': '(no output)'}

    # Detect table format (pipe-separated values)
    if '|' in lines[0]:
        html = self._create_html_table(lines)
        return {
            'text/html': html,
            'text/plain': output  # Fallback for non-HTML viewers
        }

    return {'text/plain': output}

def _create_html_table(self, lines: List[str]) -> str:
    """Convert pipe-separated output to HTML table"""
    html = ['<style>']
    html.append('''
        .expocli-table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
        }
        .expocli-table th {
            background-color: #2196F3;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        .expocli-table td {
            padding: 8px 10px;
            border-bottom: 1px solid #ddd;
        }
        .expocli-table tr:hover {
            background-color: #f5f5f5;
        }
        .expocli-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .expocli-result-count {
            color: #666;
            font-style: italic;
            margin-top: 5px;
        }
    ''')
    html.append('</style>')
    html.append('<table class="expocli-table">')

    # Parse header and data rows
    for i, line in enumerate(lines):
        if 'row(s) returned' in line:
            html.append('</table>')
            html.append(f'<div class="expocli-result-count">{line}</div>')
            break

        cells = [cell.strip() for cell in line.split('|')]

        if i == 0:  # Header row
            html.append('<thead><tr>')
            for cell in cells:
                html.append(f'<th>{cell}</th>')
            html.append('</tr></thead><tbody>')
        else:  # Data row
            html.append('<tr>')
            for cell in cells:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')

    html.append('</tbody></table>')
    return ''.join(html)
```

**Impact:** 🔥🔥🔥 Much better visual output
**Effort:** 2-3 hours

---

#### 1.2 Progress Indicator for Long Queries

**Current:** No feedback during execution
**Enhancement:** Show spinner/progress for queries taking >2 seconds

**Implementation:**

```python
import threading
import time

def _execute_query(self, query: str) -> Dict[str, Any]:
    """Execute query with progress indicator"""

    # Start progress indicator in separate thread
    progress_event = threading.Event()
    progress_thread = threading.Thread(
        target=self._show_progress,
        args=(progress_event,)
    )
    progress_thread.start()

    try:
        result = subprocess.run(
            [self.expocli_path, query],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        # ... rest of implementation
    finally:
        progress_event.set()  # Stop progress indicator
        progress_thread.join()

    return result

def _show_progress(self, stop_event: threading.Event):
    """Show progress indicator"""
    time.sleep(2)  # Wait 2s before showing
    if stop_event.is_set():
        return

    self.send_response(
        self.iopub_socket,
        'stream',
        {'name': 'stdout', 'text': '⏳ Executing query...\n'}
    )
```

**Impact:** 🔥🔥 Better UX for long queries
**Effort:** 1-2 hours

---

#### 1.3 Enhanced Error Messages

**Current:** Raw stderr output
**Enhancement:** Formatted errors with helpful suggestions

**Implementation:**

```python
def _format_error(self, error: str, query: str) -> str:
    """Format error messages with helpful suggestions"""

    error_hints = {
        'file not found': '💡 Tip: Check that the file path is correct and the file exists.',
        'syntax error': '💡 Tip: Review your query syntax. Use "help" for syntax reference.',
        'permission denied': '💡 Tip: Check file permissions or run with appropriate access.',
        'timeout': '💡 Tip: Try adding a LIMIT clause or filtering with WHERE to reduce results.',
    }

    formatted = [
        '❌ <b>Query Error</b>',
        '',
        '<div style="background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">',
        f'<code>{error}</code>',
        '</div>',
        ''
    ]

    # Add hints based on error type
    error_lower = error.lower()
    for pattern, hint in error_hints.items():
        if pattern in error_lower:
            formatted.append(hint)
            break

    return '\n'.join(formatted)
```

**Impact:** 🔥🔥 Easier debugging
**Effort:** 1 hour

---

### 🟡 Priority 2: High Impact, Medium Complexity

#### 2.1 Magic Commands

**Enhancement:** Useful % commands for common operations

**Implementation:**

```python
def _handle_magic(self, code: str, silent: bool) -> Dict[str, Any]:
    """Handle magic commands"""

    parts = code.strip().split(maxsplit=1)
    magic_cmd = parts[0][1:]  # Remove %
    magic_arg = parts[1] if len(parts) > 1 else ''

    magic_handlers = {
        'pwd': self._magic_pwd,
        'ls': self._magic_ls,
        'cd': self._magic_cd,
        'set_timeout': self._magic_set_timeout,
        'schema': self._magic_schema,
        'help': self._magic_help,
    }

    handler = magic_handlers.get(magic_cmd)
    if handler:
        return handler(magic_arg, silent)

    # Unknown magic
    if not silent:
        self.send_response(
            self.iopub_socket,
            'stream',
            {
                'name': 'stderr',
                'text': f'Unknown magic command: %{magic_cmd}\n'
                       f'Available: {", ".join("%" + k for k in magic_handlers.keys())}'
            }
        )

    return {'status': 'ok', 'execution_count': self.execution_count,
            'payload': [], 'user_expressions': {}}

def _magic_pwd(self, arg: str, silent: bool) -> Dict[str, Any]:
    """Show current working directory"""
    if not silent:
        self.send_response(
            self.iopub_socket,
            'stream',
            {'name': 'stdout', 'text': f'{os.getcwd()}\n'}
        )
    return {'status': 'ok', 'execution_count': self.execution_count,
            'payload': [], 'user_expressions': {}}

def _magic_cd(self, arg: str, silent: bool) -> Dict[str, Any]:
    """Change working directory"""
    try:
        os.chdir(arg)
        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stdout', 'text': f'Changed to: {os.getcwd()}\n'}
            )
    except Exception as e:
        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stderr', 'text': f'Error: {str(e)}\n'}
            )

    return {'status': 'ok', 'execution_count': self.execution_count,
            'payload': [], 'user_expressions': {}}

def _magic_set_timeout(self, arg: str, silent: bool) -> Dict[str, Any]:
    """Set query timeout in seconds"""
    try:
        self.query_timeout = int(arg)
        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stdout',
                 'text': f'Query timeout set to {self.query_timeout} seconds\n'}
            )
    except ValueError:
        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stderr', 'text': 'Error: Timeout must be an integer\n'}
            )

    return {'status': 'ok', 'execution_count': self.execution_count,
            'payload': [], 'user_expressions': {}}
```

**Example Usage:**
```
%pwd                    # Show current directory
%cd examples           # Change directory
%set_timeout 60        # Set 60s timeout
%help                  # Show available magics
```

**Impact:** 🔥🔥🔥 Improves workflow efficiency
**Effort:** 3-4 hours

---

#### 2.2 Tab Completion

**Enhancement:** Auto-complete file paths and SQL keywords

**Implementation:**

```python
def do_complete(self, code: str, cursor_pos: int) -> Dict[str, Any]:
    """Handle tab completion"""

    # Get the text before cursor
    text = code[:cursor_pos]

    # Find the word being completed
    match = re.search(r'(\S+)$', text)
    if not match:
        return {'status': 'ok', 'matches': [],
                'cursor_start': cursor_pos, 'cursor_end': cursor_pos,
                'metadata': {}}

    word = match.group(1)
    cursor_start = match.start(1)

    # SQL keywords
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'LIMIT',
        'GROUP', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
        'DISTINCT', 'AND', 'OR', 'NOT', 'ASC', 'DESC',
        'SET', 'XSD', 'SHOW', 'CHECK', 'GENERATE', 'XML'
    ]

    matches = []

    # Check if completing a file path
    if '/' in word or word.startswith('.'):
        # File path completion
        matches = self._complete_file_path(word)
    else:
        # Keyword completion
        matches = [kw for kw in keywords if kw.lower().startswith(word.lower())]

    return {
        'status': 'ok',
        'matches': matches,
        'cursor_start': cursor_start,
        'cursor_end': cursor_pos,
        'metadata': {}
    }

def _complete_file_path(self, partial_path: str) -> List[str]:
    """Complete file paths"""
    try:
        dirname = os.path.dirname(partial_path) or '.'
        basename = os.path.basename(partial_path)

        matches = []
        for entry in os.listdir(dirname):
            if entry.startswith(basename):
                full_path = os.path.join(dirname, entry)
                if os.path.isdir(full_path):
                    matches.append(full_path + '/')
                elif entry.endswith('.xml'):
                    matches.append(full_path)

        return sorted(matches)
    except:
        return []
```

**Impact:** 🔥🔥🔥 Faster query writing
**Effort:** 3-4 hours

---

#### 2.3 Query Result Caching

**Enhancement:** Cache expensive query results

**Implementation:**

```python
import hashlib
from datetime import datetime, timedelta

class ExpoCLIKernel(Kernel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expocli_path = self._find_expocli()
        self.query_cache = {}  # Cache: {query_hash: (result, timestamp)}
        self.cache_ttl = 300  # 5 minutes

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()

    def _execute_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """Execute query with caching"""

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(query)
            if cache_key in self.query_cache:
                result, timestamp = self.query_cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                    # Add cache indicator to output
                    result_copy = result.copy()
                    result_copy['output'] += '\n\n💾 (from cache)'
                    return result_copy

        # Execute query
        result = self._actual_execute_query(query)

        # Store in cache
        if use_cache and result['success']:
            cache_key = self._get_cache_key(query)
            self.query_cache[cache_key] = (result, datetime.now())

        return result
```

**Impact:** 🔥🔥 Faster re-execution
**Effort:** 2 hours

---

### 🔵 Priority 3: Nice to Have

#### 3.1 Syntax Highlighting

**Enhancement:** Custom CodeMirror mode for ExpoCLI syntax

**Implementation:** Create `expocli_kernel/codemirror-mode.js`:

```javascript
// ExpoCLI syntax highlighting for CodeMirror
CodeMirror.defineMode("expocli-sql", function() {
    var keywords = /^(SELECT|FROM|WHERE|ORDER|BY|LIMIT|GROUP|DISTINCT|AND|OR|NOT|ASC|DESC|SET|XSD|SHOW|CHECK|GENERATE|XML)$/i;
    var functions = /^(COUNT|SUM|AVG|MIN|MAX|FILE_NAME)$/i;

    return {
        token: function(stream, state) {
            if (stream.eatSpace()) return null;

            // Strings
            if (stream.match(/^'.*?'/)) return "string";
            if (stream.match(/^".*?"/)) return "string";

            // Numbers
            if (stream.match(/^[0-9]+(\.[0-9]+)?/)) return "number";

            // XML attributes (@category)
            if (stream.match(/^@\w+/)) return "attribute";

            // Comments
            if (stream.match(/^--.*$/)) return "comment";

            // Keywords
            var word = stream.match(/^\w+/);
            if (word) {
                if (keywords.test(word[0])) return "keyword";
                if (functions.test(word[0])) return "builtin";
            }

            stream.next();
            return null;
        }
    };
});
```

Update `expocli_kernel/kernelspec/kernel.json`:

```json
{
  "language_info": {
    "codemirror_mode": {
      "name": "expocli-sql",
      "version": 1
    }
  }
}
```

**Impact:** 🔥 Better code readability
**Effort:** 4-6 hours

---

#### 3.2 Pandas Integration

**Enhancement:** Convert results to DataFrames

**Implementation:**

```python
def _magic_to_pandas(self, arg: str, silent: bool) -> Dict[str, Any]:
    """Convert last result to pandas DataFrame"""
    try:
        import pandas as pd

        if not hasattr(self, '_last_result'):
            raise ValueError("No query result available")

        # Parse the table output
        df = self._parse_to_dataframe(self._last_result)

        # Store in user namespace (if possible)
        var_name = arg or 'df'
        self.shell.user_ns[var_name] = df

        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stdout',
                 'text': f'DataFrame stored in variable: {var_name}\n'
                        f'Shape: {df.shape}\n'}
            )
    except ImportError:
        if not silent:
            self.send_response(
                self.iopub_socket,
                'stream',
                {'name': 'stderr',
                 'text': 'Error: pandas not installed. Run: pip install pandas\n'}
            )

    return {'status': 'ok', 'execution_count': self.execution_count,
            'payload': [], 'user_expressions': {}}
```

**Impact:** 🔥🔥 Enables data analysis
**Effort:** 4-5 hours

---

#### 3.3 Interactive Visualizations

**Enhancement:** Quick plotting of results

**Example Usage:**

```python
# In notebook cell:
SELECT name, price FROM examples/books.xml

# In next cell with magic:
%plot price --kind bar --title "Book Prices"
```

**Impact:** 🔥🔥 Data exploration
**Effort:** 6-8 hours

---

## Implementation Priority

**Phase 1 (Week 1):**
1. HTML Table Output - 3 hours
2. Enhanced Error Messages - 1 hour
3. Progress Indicator - 2 hours

**Phase 2 (Week 2):**
4. Magic Commands - 4 hours
5. Tab Completion - 4 hours

**Phase 3 (Week 3):**
6. Query Caching - 2 hours
7. Pandas Integration - 5 hours

**Phase 4 (Optional):**
8. Syntax Highlighting - 6 hours
9. Visualizations - 8 hours

## Testing Strategy

Create `tests/test_kernel_enhancements.py`:

```python
import unittest
from expocli_kernel import ExpoCLIKernel

class TestKernelEnhancements(unittest.TestCase):
    def setUp(self):
        self.kernel = ExpoCLIKernel()

    def test_html_output_formatting(self):
        """Test HTML table generation"""
        output = "name | price\nBook1 | $10\n1 row(s) returned."
        result = self.kernel._format_output(output)
        self.assertIn('text/html', result)
        self.assertIn('expocli-table', result['text/html'])

    def test_magic_commands(self):
        """Test magic command execution"""
        result = self.kernel._handle_magic('%pwd', False)
        self.assertEqual(result['status'], 'ok')

    def test_tab_completion(self):
        """Test tab completion"""
        result = self.kernel.do_complete('SELECT na', 9)
        # Should complete to 'name' or show suggestions
        self.assertGreater(len(result['matches']), 0)
```

## Documentation Updates

Update `JUPYTER_KERNEL.md` with:
- Magic command reference
- HTML output examples
- Best practices for large queries
- Caching behavior explanation

## User Benefits Summary

| Enhancement | Time Saved | Learning Curve | User Satisfaction |
|-------------|-----------|----------------|-------------------|
| HTML Tables | Medium | Low | ⭐⭐⭐⭐⭐ |
| Magic Commands | High | Medium | ⭐⭐⭐⭐ |
| Tab Completion | High | Low | ⭐⭐⭐⭐⭐ |
| Error Messages | Medium | Low | ⭐⭐⭐⭐ |
| Progress Indicator | Low | None | ⭐⭐⭐ |
| Caching | High | Low | ⭐⭐⭐⭐ |
| Pandas | Very High | Medium | ⭐⭐⭐⭐⭐ |
| Syntax Highlighting | Low | None | ⭐⭐⭐ |
| Visualizations | Very High | Medium | ⭐⭐⭐⭐⭐ |

---

**Next Steps:**
1. Review this plan with the team
2. Create GitHub issues for each enhancement
3. Start with Phase 1 (high impact, low effort)
4. Gather user feedback after each phase
