#!/usr/bin/env python3
"""
Test script to measure formatting overhead (without full kernel import)
"""

import time
import subprocess
import re

def execute_query(query):
    """Execute a query using the C++ backend"""
    result = subprocess.run(
        ['/home/user/ariane-xml/ariane-xml-c-kernel/build/ariane-xml', query],
        capture_output=True,
        text=True,
        cwd='/home/user/ariane-xml'
    )
    return result.stdout

def simple_format_check(output):
    """Simulate basic formatting checks (like kernel does)"""
    if not output:
        return False

    lines = output.strip().split('\n')

    # Check if this looks like a table (kernel does this)
    is_table = False
    if len(lines) >= 2:
        if '|' in lines[0]:
            is_table = True
        elif len(lines[1].strip()) > 0 and lines[1].strip().replace('-', '').replace(' ', '') == '':
            is_table = True

    return is_table

def convert_to_html_minimal(output):
    """Minimal HTML conversion (simulates what kernel does)"""
    lines = output.strip().split('\n')

    # Parse header
    if '|' in lines[0]:
        header = [cell.strip() for cell in lines[0].split('|') if cell.strip()]

    # Parse data rows
    data_rows = []
    for line in lines[1:]:
        if 'rows returned' in line:
            continue
        if line.strip():
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                data_rows.append(cells)

    # Generate minimal HTML (kernel generates much more)
    html = '<table>'
    html += '<thead><tr>' + ''.join(f'<th>{h}</th>' for h in header) + '</tr></thead>'
    html += '<tbody>'
    for row in data_rows:
        html += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
    html += '</tbody></table>'

    return html

def test_with_formatting():
    """Test with formatting simulation"""
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

        # Formatting
        start_format = time.time()
        is_table = simple_format_check(output)
        if is_table:
            html = convert_to_html_minimal(output)
        format_time = (time.time() - start_format) * 1000
        times_format.append(format_time)

        times_total.append(exec_time + format_time)

    return times_exec, times_format, times_total

if __name__ == '__main__':
    print("Testing Ariane-XML Formatting Overhead")
    print("=" * 60)

    times_exec, times_format, times_total = test_with_formatting()

    avg_exec = sum(times_exec) / len(times_exec)
    avg_format = sum(times_format) / len(times_format)
    avg_total = sum(times_total) / len(times_total)

    print(f"\nExecution time (C++ backend):")
    print(f"  Average: {avg_exec:.2f} ms")
    print(f"  Min: {min(times_exec):.2f} ms")
    print(f"  Max: {max(times_exec):.2f} ms")

    print(f"\nFormatting time (HTML generation):")
    print(f"  Average: {avg_format:.2f} ms")
    print(f"  Min: {min(times_format):.2f} ms")
    print(f"  Max: {max(times_format):.2f} ms")

    print(f"\nTotal time:")
    print(f"  Average: {avg_total:.2f} ms")
    print(f"  Min: {min(times_total):.2f} ms")
    print(f"  Max: {max(times_total):.2f} ms")

    overhead_pct = (avg_format / avg_exec) * 100
    print(f"\nFormatting overhead: {overhead_pct:.1f}% of execution time")

    if avg_total < 100:
        print(f"\n✓ Performance is EXCELLENT (< 100ms)")
    elif avg_total < 200:
        print(f"\n✓ Performance is GOOD (< 200ms)")
    else:
        print(f"\n⚠ Performance may be slow (> 200ms)")
