# Quick Start Guide - Running Tests

## Running the Test Suite

You can run the test suite from **anywhere** on your system:

```bash
# From project root
./ariane-xml-tests/run_tests.sh

# From any directory (using absolute or relative path)
/path/to/Ariane-XML/ariane-xml-tests/run_tests.sh

# Or if you're in a different directory
cd /tmp
~/Ariane-XML/ariane-xml-tests/run_tests.sh
```

## Binary Detection

The test script is **smart** about finding the Ariane-XML binary with multiple strategies:

1. **First**: Checks for `./ariane-xml-c-kernel/build/ariane-xml` (local build - best for testing)
2. **Second**: Checks if `ariane-xml` is in your PATH (system-installed)
3. **Third**: Falls back to `./ariane-xml-scripts/ariane-xml.sh` wrapper script (Docker-based execution)
4. **Finally**: Offers to build it for you if not found

You'll see which one it's using:
```
Working directory: /home/user/Ariane-XML
Using wrapper script: ./ariane-xml-scripts/ariane-xml.sh
```

or

```
Working directory: /home/user/Ariane-XML
Using ariane-xml from PATH: /usr/local/bin/ariane-xml
```

or

```
Working directory: /home/user/Ariane-XML
Using local build: ./ariane-xml-c-kernel/build/ariane-xml
```

### Important: Aliases Don't Work in Scripts

If you have an alias like:
```bash
alias ariane-xml='/path/to/ariane-xml-scripts/ariane-xml.sh'
```

This alias **won't work** in the test script because:
- Aliases are only loaded in interactive shells
- Test scripts run in non-interactive mode
- `.bashrc` aliases aren't available

**Solution**: The test script will automatically find `ariane-xml-scripts/ariane-xml.sh` in the project, so you don't need the alias for testing!

## First Time Setup

If the binary hasn't been built and isn't in PATH, the test script will:
1. Detect the missing binary
2. Check if you have `cmake` installed
3. Ask if you want to build it automatically
4. Build the project for you (if you answer 'y')

Example:
```
╔════════════════════════════════════════════════════════════════╗
║           Ariane-XML Comprehensive Test Suite v1.0               ║
╚════════════════════════════════════════════════════════════════╝

Working directory: /home/user/Ariane-XML

ERROR: Ariane-XML binary not found
The binary is not in PATH and not found at ./ariane-xml-c-kernel/build/ariane-xml

Options:
  1. Install ariane-xml to your PATH, or
  2. Build locally in ./ariane-xml-c-kernel/build/

Would you like to build it locally now? (y/n)
```

Type `y` and press Enter, and the build will happen automatically!

## Manual Build

If you prefer to build manually:

```bash
mkdir -p ariane-xml-c-kernel/build
cd ariane-xml-c-kernel/build
cmake ..
make -j4
```

## What the Test Script Does

1. **Auto-detects project root** - Works from any directory
2. **Shows working directory** - So you know where it's running
3. **Checks for binary** - Verifies ariane-xml is built
4. **Offers auto-build** - Builds project if needed
5. **Runs all tests** - 33 comprehensive tests
6. **Shows results** - Color-coded pass/fail with summary

## Expected Output

When all tests pass:
```
✓ ALL TESTS PASSED

Total Tests:         33
Passed:              33
Failed:              0
Duration:            2 seconds
Success Rate: 100%
```

## Troubleshooting

### "ERROR: Could not find project root directory"
The script couldn't find CMakeLists.txt. Make sure you're running the correct script:
```bash
# Correct
/path/to/Ariane-XML/ariane-xml-tests/run_tests.sh

# Not
/path/to/Ariane-XML/run_tests.sh  # Wrong location
```

### "ERROR: Ariane-XML binary not found"
Choose option 'y' to auto-build, or build manually:
```bash
cd /path/to/Ariane-XML
mkdir -p ariane-xml-c-kernel/build && cd ariane-xml-c-kernel/build && cmake .. && make
```

### Tests fail after code changes
This is normal! The tests are working correctly by detecting issues. Check:
1. The failure log: `ariane-xml-tests/logs/failures.log`
2. Individual test output files in `ariane-xml-tests/output/`

## Adding to Your Workflow

### Git Hook
Add to `.git/hooks/pre-push`:
```bash
#!/bin/bash
./ariane-xml-tests/run_tests.sh || exit 1
```

### CI/CD
```yaml
test:
  script:
    - ./ariane-xml-tests/run_tests.sh
  artifacts:
    when: on_failure
    paths:
      - ariane-xml-tests/logs/
```

### Make Target
Add to your Makefile:
```make
test:
	./ariane-xml-tests/run_tests.sh
```

Then run: `make test`
