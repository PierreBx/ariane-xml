#!/usr/bin/env python3
"""
Test script to measure Jupyter kernel performance overhead
"""

import sys
import time
import subprocess

# Add the kernel to the path
sys.path.insert(0, '/home/user/ariane-xml/ariane-xml-jupyter-kernel')

# Import kernel modules
from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel

def test_direct_execution():
    """Test direct C++ execution time"""
    times = []
    for i in range(10):
        start = time.time()
        result = subprocess.run(
            ['/home/user/ariane-xml/ariane-xml-c-kernel/build/ariane-xml',
             'SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"'],
            capture_output=True,
            text=True,
            cwd='/home/user/ariane-xml'
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    return times

def test_kernel_execution():
    """Test kernel execution time (simulates Jupyter execution path)"""
    # Create a kernel instance
    kernel = ArianeXMLKernel()

    times = []
    for i in range(10):
        start = time.time()
        # Execute query through kernel's method
        result = kernel._execute_query('SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"')
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    return times

def test_kernel_with_formatting():
    """Test kernel with full formatting (HTML generation)"""
    kernel = ArianeXMLKernel()

    times = []
    for i in range(10):
        start = time.time()
        # Execute query
        result = kernel._execute_query('SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"')
        # Format output (this is where HTML generation happens)
        if result['success'] and result['output']:
            formatted = kernel._format_output(result['output'], query='SELECT food/name, food/price FROM "ariane-xml-examples/test.xml"')
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    return times

def print_stats(name, times):
    """Print statistics for a set of times"""
    avg = sum(times) / len(times)
    min_t = min(times)
    max_t = max(times)
    print(f"\n{name}:")
    print(f"  Average: {avg:.2f} ms")
    print(f"  Min: {min_t:.2f} ms")
    print(f"  Max: {max_t:.2f} ms")
    print(f"  Range: {max_t - min_t:.2f} ms")

if __name__ == '__main__':
    print("Testing Ariane-XML Jupyter Kernel Performance")
    print("=" * 60)

    print("\n1. Direct C++ Execution (baseline)")
    direct_times = test_direct_execution()
    print_stats("Direct C++ Backend", direct_times)

    print("\n2. Through Kernel _execute_query (adds subprocess overhead)")
    kernel_times = test_kernel_execution()
    print_stats("Kernel _execute_query", kernel_times)
    overhead_1 = sum(kernel_times) / len(kernel_times) - sum(direct_times) / len(direct_times)
    print(f"  Overhead: {overhead_1:.2f} ms")

    print("\n3. With Full Formatting (HTML table generation)")
    formatted_times = test_kernel_with_formatting()
    print_stats("Kernel with Formatting", formatted_times)
    overhead_2 = sum(formatted_times) / len(formatted_times) - sum(direct_times) / len(direct_times)
    print(f"  Total Overhead: {overhead_2:.2f} ms")
    print(f"  Formatting Overhead: {overhead_2 - overhead_1:.2f} ms")

    print("\n" + "=" * 60)
    print("Summary:")
    avg_direct = sum(direct_times) / len(direct_times)
    avg_formatted = sum(formatted_times) / len(formatted_times)
    slowdown = (avg_formatted / avg_direct - 1) * 100
    print(f"  C++ Backend: {avg_direct:.2f} ms")
    print(f"  Full Kernel: {avg_formatted:.2f} ms")
    print(f"  Slowdown: {slowdown:.1f}%")
