#!/usr/bin/env python3
"""Test script to verify the Jupyter kernel works correctly"""

import sys
sys.path.insert(0, '/home/user/ariane-xml/ariane-xml-jupyter-kernel')

from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel

def test_kernel():
    """Test the kernel with the example query"""
    print("Testing Ariane-XML Jupyter Kernel...")
    print("=" * 50)

    # Create kernel instance
    kernel = ArianeXMLKernel()

    print(f"Binary path: {kernel.ariane_xml_path}")
    print(f"Working directory: {kernel.working_directory}")
    print()

    # Test queries
    queries = [
        'SELECT COUNT(.name) FROM examples/test.xml;',
        'SELECT COUNT(.name) FROM "examples/test.xml";',
        'SELECT .name FROM examples/test.xml;',
    ]

    for query in queries:
        print(f"Query: {query}")
        result = kernel._execute_query(query)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Output:\n{result['output']}")
        else:
            print(f"Error: {result['error']}")
        print("-" * 50)

if __name__ == '__main__':
    test_kernel()
