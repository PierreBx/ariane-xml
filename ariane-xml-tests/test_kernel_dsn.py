#!/usr/bin/env python3
"""
Quick test to verify DSN MODE detection in Jupyter kernel
"""

import sys
sys.path.insert(0, '/home/user/ariane-xml/ariane-xml-jupyter-kernel')

from ariane_xml_jupyter_kernel.kernel import ArianeXMLKernel

# Create a kernel instance (without full Jupyter initialization)
kernel = ArianeXMLKernel.__new__(ArianeXMLKernel)
kernel.dsn_mode = False
kernel.dsn_version = None

# Test DSN command detection
test_cases = [
    ("SET MODE DSN", True, "Should detect SET MODE DSN"),
    ("SET DSN_VERSION P26", True, "Should detect SET DSN_VERSION"),
    ("DESCRIBE 01_001", True, "Should detect DESCRIBE"),
    ("TEMPLATE LIST", True, "Should detect TEMPLATE"),
    ("COMPARE P25 P26", True, "Should detect COMPARE"),
    ("SELECT * FROM test.xml", False, "Should NOT detect regular query"),
    ("SHOW MODE", True, "Should detect SHOW MODE"),
]

print("Testing DSN Command Detection:")
print("=" * 60)

all_passed = True
for query, expected, description in test_cases:
    result = kernel._is_dsn_command(query)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_passed = False
    print(f"{status}: {description}")
    print(f"   Query: '{query}'")
    print(f"   Expected: {expected}, Got: {result}")
    print()

# Test state updates
print("Testing DSN State Updates:")
print("=" * 60)

# Test SET MODE DSN
kernel._update_dsn_state("SET MODE DSN")
if kernel.dsn_mode:
    print("✓ PASS: SET MODE DSN activates DSN mode")
else:
    print("✗ FAIL: SET MODE DSN should activate DSN mode")
    all_passed = False

# Test SET DSN_VERSION P26
kernel._update_dsn_state("SET DSN_VERSION P26")
if kernel.dsn_version == 'P26':
    print("✓ PASS: SET DSN_VERSION P26 sets version to P26")
else:
    print(f"✗ FAIL: Expected P26, got {kernel.dsn_version}")
    all_passed = False

# Test SET MODE STANDARD
kernel._update_dsn_state("SET MODE STANDARD")
if not kernel.dsn_mode and kernel.dsn_version is None:
    print("✓ PASS: SET MODE STANDARD deactivates DSN mode and clears version")
else:
    print(f"✗ FAIL: Expected dsn_mode=False, version=None, got {kernel.dsn_mode}, {kernel.dsn_version}")
    all_passed = False

print()

# Test badge generation
print("Testing DSN Mode Badge:")
print("=" * 60)

kernel.dsn_mode = False
kernel.dsn_version = None
badge = kernel._get_dsn_mode_badge()
if badge == "":
    print("✓ PASS: No badge when DSN mode is off")
else:
    print(f"✗ FAIL: Expected empty badge, got '{badge}'")
    all_passed = False

kernel.dsn_mode = True
kernel.dsn_version = None
badge = kernel._get_dsn_mode_badge()
if "DSN MODE" in badge:
    print(f"✓ PASS: Badge shows DSN MODE: '{badge}'")
else:
    print(f"✗ FAIL: Expected DSN MODE in badge, got '{badge}'")
    all_passed = False

kernel.dsn_mode = True
kernel.dsn_version = 'P26'
badge = kernel._get_dsn_mode_badge()
if "DSN MODE" in badge and "P26" in badge:
    print(f"✓ PASS: Badge shows DSN MODE with version: '{badge}'")
else:
    print(f"✗ FAIL: Expected DSN MODE [P26] in badge, got '{badge}'")
    all_passed = False

print()
print("=" * 60)
if all_passed:
    print("✓ All tests passed!")
    sys.exit(0)
else:
    print("✗ Some tests failed")
    sys.exit(1)
