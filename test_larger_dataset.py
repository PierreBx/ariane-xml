#!/usr/bin/env python3
"""
Test performance with a larger dataset
"""

import time
import subprocess
import sys

def execute_query(query):
    """Execute query and measure time"""
    start = time.time()
    result = subprocess.run(
        ['/home/user/ariane-xml/ariane-xml-c-kernel/build/ariane-xml', query],
        capture_output=True,
        text=True,
        cwd='/home/user/ariane-xml'
    )
    elapsed = (time.time() - start) * 1000
    return result.stdout, result.stderr, elapsed

def count_rows(output):
    """Count number of rows in output"""
    for line in output.split('\n'):
        if 'rows returned' in line or 'row(s) returned' in line:
            try:
                parts = line.split()
                return int(parts[0])
            except:
                pass
    return 0

if __name__ == '__main__':
    print("Testing Performance with Various Dataset Sizes")
    print("=" * 60)

    # Test different queries with varying result sizes
    test_cases = [
        ('Small result (5 rows)', 'SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"'),
        ('Books dataset', 'SELECT book/title, book/author, book/price FROM "ariane-xml-examples/books.xml"'),
        ('Products dataset', 'SELECT product/name, product/price FROM "ariane-xml-examples/products.xml"'),
    ]

    for name, query in test_cases:
        print(f"\n{name}:")
        print(f"  Query: {query[:60]}...")

        # Run query once to get row count
        output, error, _ = execute_query(query)

        if error and 'Error' in error:
            print(f"  ⚠ Error: {error[:100]}")
            continue

        row_count = count_rows(output)
        output_size = len(output)

        # Measure performance over multiple runs
        times = []
        for i in range(5):
            _, _, elapsed = execute_query(query)
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  Rows returned: {row_count}")
        print(f"  Output size: {output_size:,} bytes ({output_size/1024:.1f} KB)")
        print(f"  Average time: {avg_time:.2f} ms")
        print(f"  Range: {min_time:.2f} - {max_time:.2f} ms")

        if row_count > 0:
            time_per_row = avg_time / row_count
            print(f"  Time per row: {time_per_row:.3f} ms")

        if avg_time < 50:
            status = "✓ EXCELLENT"
        elif avg_time < 100:
            status = "✓ VERY GOOD"
        elif avg_time < 200:
            status = "✓ GOOD"
        else:
            status = "⚠ May be slow"

        print(f"  Status: {status}")

    print("\n" + "=" * 60)
    print("Conclusion:")
    print("If all tests show < 200ms, performance is good for Jupyter use.")
