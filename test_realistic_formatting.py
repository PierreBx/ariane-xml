#!/usr/bin/env python3
"""
Test realistic formatting overhead including full CSS/HTML like the actual kernel
"""

import time
import subprocess

# Large CSS that the kernel embeds in every table output
FULL_CSS = '''
<style>
    .ariane-xml-container {
        --ariane-bg: #ffffff;
        --ariane-bg-alt: #f6f8fa;
        --ariane-bg-hover: #f0f2f4;
        --ariane-text: #24292e;
        --ariane-text-secondary: #586069;
        --ariane-border: #e1e4e8;
        --ariane-header-bg: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        --ariane-header-border: #4b5563;
        --ariane-numeric: #374151;
        --ariane-success: #22863a;
        --ariane-shadow: rgba(0,0,0,0.12);
        --ariane-shadow-strong: rgba(0,0,0,0.24);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
        margin: 15px 0;
    }
    @media (prefers-color-scheme: dark) {
        .ariane-xml-container {
            --ariane-bg: #21262d;
            --ariane-bg-alt: #30363d;
            --ariane-bg-hover: #3a424a;
            --ariane-text: #c9d1d9;
            --ariane-text-secondary: #8b949e;
            --ariane-border: #30363d;
            --ariane-header-bg: linear-gradient(135deg, #4b5563 0%, #374151 100%);
            --ariane-header-border: #374151;
            --ariane-numeric: #a5b4c4;
            --ariane-success: #3fb950;
            --ariane-shadow: rgba(0,0,0,0.3);
            --ariane-shadow-strong: rgba(0,0,0,0.5);
        }
    }
    [data-jp-theme-light="false"] .ariane-xml-container,
    .jp-Notebook.jp-mod-dark .ariane-xml-container,
    body.theme-dark .ariane-xml-container {
        --ariane-bg: #21262d;
        --ariane-bg-alt: #30363d;
        --ariane-bg-hover: #3a424a;
        --ariane-text: #c9d1d9;
        --ariane-text-secondary: #8b949e;
        --ariane-border: #30363d;
        --ariane-header-bg: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        --ariane-header-border: #374151;
        --ariane-numeric: #a5b4c4;
        --ariane-success: #3fb950;
        --ariane-shadow: rgba(0,0,0,0.3);
        --ariane-shadow-strong: rgba(0,0,0,0.5);
    }
    .ariane-xml-table {
        border-collapse: collapse;
        width: 100%;
        background: var(--ariane-bg);
        box-shadow: 0 1px 3px var(--ariane-shadow), 0 1px 2px var(--ariane-shadow-strong);
        border-radius: 4px;
        overflow: hidden;
    }
    .ariane-xml-table th {
        background: var(--ariane-header-bg);
        color: white;
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid var(--ariane-header-border);
    }
    .ariane-xml-table td {
        padding: 10px 16px;
        border-bottom: 1px solid var(--ariane-border);
        font-size: 14px;
        color: var(--ariane-text);
    }
    .ariane-xml-table tr:last-child td {
        border-bottom: none;
    }
    .ariane-xml-table tr:hover {
        background-color: var(--ariane-bg-hover);
    }
    .ariane-xml-table tr:nth-child(even) {
        background-color: var(--ariane-bg-alt);
    }
    .ariane-xml-table td.numeric {
        text-align: right;
        font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        color: var(--ariane-numeric);
    }
    .ariane-xml-result-count {
        color: var(--ariane-text-secondary);
        font-size: 13px;
        font-style: italic;
        margin-top: 8px;
        padding: 8px 12px;
        background: var(--ariane-bg-alt);
        border-radius: 4px;
        display: inline-block;
    }
    .ariane-xml-result-count::before {
        content: "✓ ";
        color: var(--ariane-success);
        font-weight: bold;
    }
</style>
'''

def execute_query(query):
    """Execute query via C++ backend"""
    result = subprocess.run(
        ['/home/user/ariane-xml/ariane-xml-c-kernel/build/ariane-xml', query],
        capture_output=True,
        text=True,
        cwd='/home/user/ariane-xml'
    )
    return result.stdout

def escape_html(text):
    """Escape HTML special characters"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def is_numeric(value):
    """Check if value is numeric"""
    cleaned = value.replace('$', '').replace(',', '').strip()
    try:
        float(cleaned)
        return True
    except ValueError:
        return False

def create_full_html_table(output):
    """Generate full HTML table like the kernel does"""
    lines = output.strip().split('\n')
    html = []

    # Add the large CSS block
    html.append(FULL_CSS)

    table_id = f"table_{int(time.time() * 1000)}"

    html.append('<div class="ariane-xml-container">')
    html.append(f'<table class="ariane-xml-table" id="result_{table_id}">')

    # Parse rows
    table_rows = []
    result_count = None

    for line in lines:
        if 'row(s) returned' in line or 'rows returned' in line:
            result_count = line.strip()
            continue
        if line.strip():
            table_rows.append(line)

    # Process table rows (fixed-width format)
    if table_rows and len(table_rows) >= 2:
        # Find separator line
        separator_idx = -1
        for i, line in enumerate(table_rows):
            if line.strip() and line.strip().replace('-', '').replace(' ', '') == '':
                separator_idx = i
                break

        if separator_idx > 0:
            # Parse header
            header_line = table_rows[separator_idx - 1]
            separator = table_rows[separator_idx]

            # Find column positions
            col_positions = []
            in_column = False
            start_pos = 0

            for i, char in enumerate(separator):
                if char == '-':
                    if not in_column:
                        start_pos = i
                        in_column = True
                else:
                    if in_column:
                        col_positions.append((start_pos, i))
                        in_column = False

            if in_column:
                col_positions.append((start_pos, len(separator)))

            # Extract header cells
            headers = []
            for start, end in col_positions:
                cell = header_line[start:end].strip() if start < len(header_line) else ""
                headers.append(cell)

            # Generate header HTML
            html.append('<thead><tr>')
            for header in headers:
                html.append(f'<th>{escape_html(header)}</th>')
            html.append('</tr></thead>')

            # Generate data rows
            html.append('<tbody>')
            for row_idx in range(separator_idx + 1, len(table_rows)):
                line = table_rows[row_idx]
                html.append('<tr>')
                for start, end in col_positions:
                    cell = line[start:end].strip() if start < len(line) else ""
                    cell_class = 'numeric' if is_numeric(cell) else ''
                    class_attr = f' class="{cell_class}"' if cell_class else ''
                    html.append(f'<td{class_attr}>{escape_html(cell)}</td>')
                html.append('</tr>')
            html.append('</tbody>')

    html.append('</table>')

    if result_count:
        html.append(f'<div class="ariane-xml-result-count">{escape_html(result_count)}</div>')

    html.append('</div>')

    return ''.join(html)

def test_realistic_formatting():
    """Test with realistic full HTML generation"""
    query = 'SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"'

    times_exec = []
    times_format = []
    times_total = []

    for i in range(10):
        # Execution
        start_exec = time.time()
        output = execute_query(query)
        exec_time = (time.time() - start_exec) * 1000
        times_exec.append(exec_time)

        # Full HTML formatting (like kernel does)
        start_format = time.time()
        html = create_full_html_table(output)
        format_time = (time.time() - start_format) * 1000
        times_format.append(format_time)

        times_total.append(exec_time + format_time)

    return times_exec, times_format, times_total, html

if __name__ == '__main__':
    print("Testing Realistic Jupyter Kernel Formatting Overhead")
    print("=" * 60)

    times_exec, times_format, times_total, sample_html = test_realistic_formatting()

    avg_exec = sum(times_exec) / len(times_exec)
    avg_format = sum(times_format) / len(times_format)
    avg_total = sum(times_total) / len(times_total)

    print(f"\nC++ Backend Execution:")
    print(f"  Average: {avg_exec:.2f} ms")
    print(f"  Range: {min(times_exec):.2f} - {max(times_exec):.2f} ms")

    print(f"\nHTML Formatting (with full CSS):")
    print(f"  Average: {avg_format:.2f} ms")
    print(f"  Range: {min(times_format):.2f} - {max(times_format):.2f} ms")

    print(f"\nTotal Query Time:")
    print(f"  Average: {avg_total:.2f} ms")
    print(f"  Range: {min(times_total):.2f} - {max(times_total):.2f} ms")

    overhead_pct = (avg_format / avg_exec) * 100
    print(f"\nFormatting Overhead: {overhead_pct:.1f}% of execution time")

    html_size = len(sample_html)
    print(f"HTML Output Size: {html_size:,} bytes ({html_size/1024:.1f} KB)")

    print("\n" + "=" * 60)
    print("Analysis:")
    if avg_total < 50:
        print("✓ Performance is EXCELLENT (< 50ms)")
        print("  Users will not notice any delay")
    elif avg_total < 100:
        print("✓ Performance is VERY GOOD (< 100ms)")
        print("  Feels instant to users")
    elif avg_total < 200:
        print("✓ Performance is GOOD (< 200ms)")
        print("  Still feels responsive")
    else:
        print("⚠ Performance may feel slow (> 200ms)")

    if overhead_pct > 20:
        print(f"\n⚠ Warning: Formatting overhead is significant ({overhead_pct:.1f}%)")
        print("  Consider optimizing HTML generation or using caching for CSS")
    else:
        print(f"\n✓ Formatting overhead is acceptable ({overhead_pct:.1f}%)")
