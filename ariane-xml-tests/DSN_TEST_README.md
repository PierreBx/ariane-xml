# DSN Mode Test Suite

## Overview

The DSN mode test suite is a comprehensive test framework for validating ariane-xml's DSN (Déclaration Sociale Nominative) mode features. It automatically generates test datasets from real DSN XSD schemas and validates all DSN-specific functionality.

## Features Tested

### 1. DSN Mode Activation
- Setting DSN mode (`SET MODE DSN`)
- Showing current mode
- Switching between STANDARD and DSN modes

### 2. Schema Version Management
- P25 schema support
- P26 schema support
- Auto-detection mode
- Schema information display

### 3. DSN Types
- **FCTU** (Fin de Contrat de Travail Unique)
- **mensuelle** (Déclaration mensuelle)
- **SADV** (Signalement d'Arrêt de travail Dérogatoire pour les personnes Vulnérables)

### 4. Query Features
- Full DSN path queries
- YY_ZZZ shortcut notation
- Multiple field selection
- WHERE clauses with DSN fields
- Complex boolean logic (AND/OR)
- LIKE operator on DSN fields
- ORDER BY and LIMIT
- DISTINCT queries
- Aggregation functions (COUNT)

### 5. DSN-Specific Commands
- `DESCRIBE` command for field documentation
- Template queries
- DSN validation with `CHECK`

### 6. Performance Testing
- Query performance across different DSN types
- Multi-file processing
- P25 and P26 schema performance comparison

## Test Data

The test suite automatically generates sample XML files if they don't exist:

- **P25 FCTU**: 5 files in `ariane-xml-tests/output/dsn_test/data/p25_fctu/`
- **P25 mensuelle**: 5 files in `ariane-xml-tests/output/dsn_test/data/p25_mensuelle/`
- **P26 FCTU**: 5 files in `ariane-xml-tests/output/dsn_test/data/p26_fctu/`
- **P26 mensuelle**: 5 files in `ariane-xml-tests/output/dsn_test/data/p26_mensuelle/`
- **P26 SADV**: 5 files in `ariane-xml-tests/output/dsn_test/data/p26_sadv/`

### Data Sources

Test data is generated from official DSN XSD schemas located in:
- `ariane-xml-schemas/xsd_P25/`
- `ariane-xml-schemas/xsd_P26/`

## Running the Tests

### Using the Manager (Recommended)

```bash
# Interactive menu
./ariane-xml-manager.sh
# Select option 16: Run DSN mode test suite (Docker)

# Command-line (Docker mode)
./ariane-xml-manager.sh --test-dsn

# Command-line (Local mode)
./ariane-xml-manager.sh --test-dsn-local
```

### Direct Execution

```bash
# Docker mode
./ariane-xml-scripts/manager/test-dsn-docker.sh

# Local mode (requires ariane-xml binary in build/)
./ariane-xml-scripts/manager/test-dsn.sh

# Direct script execution
./ariane-xml-tests/dsn_test.sh
```

## Test Categories

### Phase 1: Dataset Generation
Automatically generates test datasets if not present. Reuses existing files on subsequent runs for faster execution.

### Phase 2: Mode Configuration (DSN-001 to DSN-007)
- Mode switching
- Version configuration
- Schema information display

### Phase 3: Basic Queries (DSN-101 to DSN-103)
- Full path queries on P26 FCTU
- Multi-field selection
- File counting

### Phase 4: Shortcut Notation (DSN-201 to DSN-204)
- YY_ZZZ shortcuts
- Mixed full path and shortcut queries
- WHERE with shortcuts

### Phase 5: P25 Schema (DSN-301 to DSN-303)
- P25 FCTU queries
- P25 mensuelle queries
- P25 filtering

### Phase 6: P26 All Types (DSN-401 to DSN-405)
- P26 FCTU queries
- P26 mensuelle queries
- P26 SADV queries
- Aggregations
- LIMIT clauses

### Phase 7: DESCRIBE Command (DSN-501 to DSN-503)
- Field description by shortcut
- Field description by full path
- Bloc description

### Phase 8: Templates (DSN-601 to DSN-604)
- Template listing
- Template display
- Template execution

### Phase 9: Complex Queries (DSN-701 to DSN-705)
- AND/OR operators
- LIKE patterns
- ORDER BY
- DISTINCT

### Phase 10: Validation (DSN-801 to DSN-803)
- CHECK command with DSN schemas
- Error handling
- Invalid query detection

### Phase 11: Auto-Detection (DSN-901 to DSN-902)
- P25 version auto-detection
- P26 version auto-detection

### Phase 12: Performance Tests
- Query timing across all DSN types
- Performance comparison between P25 and P26

### Phase 13: Summary
- Dataset statistics
- Storage requirements
- Test results summary

## Test Output

The test suite provides comprehensive output including:

```
=========================================
DSN MODE TEST SUITE
=========================================

This test suite validates DSN mode features:
  1. DSN mode activation and configuration
  2. Schema version auto-detection (P25/P26)
  3. DSN type detection (FCTU, mensuelle, SADV)
  4. YY_ZZZ shortcut notation
  5. Field queries with DSN paths
  6. Template queries
  7. DESCRIBE command
  8. DSN validation

Phase 1: DSN Test Data Preparation
  ✓ P25_FCTU: Using existing 5 files
  ✓ P25_MENSUELLE: Using existing 5 files
  ...

========================================
Category: 2. DSN Mode Activation and Configuration
========================================
  [DSN-001]   Set DSN mode                           ✓ PASS
  [DSN-002]   Show current mode                      ✓ PASS
  ...

========================================
Summary
========================================
Tests Passed:  XX
Tests Failed:  0
Total Tests:   XX
Success Rate:  100.00%
```

## Maintenance

### Regenerating Test Data

To force regeneration of test datasets:

```bash
rm -rf ariane-xml-tests/output/dsn_test/data/
./ariane-xml-tests/dsn_test.sh
```

### Adding New Tests

1. Follow the existing test pattern in `dsn_test.sh`
2. Use the `run_test` helper function
3. Add tests in logical categories
4. Update test counts in this README

### Updating Schema Versions

When new DSN schema versions are released:

1. Add XSD files to `ariane-xml-schemas/xsd_PXX/`
2. Update schema paths in `dsn_test.sh`
3. Add new test phases for the new version
4. Update documentation

## Requirements

- Docker (for Docker mode)
- Compiled ariane-xml binary (for local mode)
- DSN XSD schemas in `ariane-xml-schemas/`
- Sufficient disk space (~50-100MB for test data)

## Troubleshooting

### Tests Fail to Generate Data

**Problem**: Dataset generation fails

**Solution**:
1. Check that XSD files exist in `ariane-xml-schemas/`
2. Verify ariane-xml binary is compiled
3. Check disk space availability
4. Review generation logs in `ariane-xml-tests/output/dsn_test/`

### DSN Mode Not Available

**Problem**: DSN mode commands not recognized

**Solution**:
1. Ensure you're using the latest build
2. Rebuild the binary: `cd build && make clean && cmake .. && make`
3. Verify DSN mode is compiled: `ariane-xml --help`

### Slow Test Execution

**Problem**: Tests take too long

**Solution**:
1. Test data is cached after first run
2. Use fewer files: edit `NUM_FILES` variable in script
3. Run specific test phases instead of full suite

## Performance Benchmarks

Typical execution times (with cached datasets):

- **Dataset Generation**: 0s (cached) or ~10-30s (first run)
- **Full Test Suite**: ~2-5 minutes
- **Per Query**: ~0.1-0.5 seconds

## Integration

The DSN test suite integrates seamlessly with:

- Ariane-XML manager console
- CI/CD pipelines (exit code 0 on success, 1 on failure)
- Docker environments
- Local development environments

## See Also

- [DSN Mode Design](../DSN_MODE_DESIGN.md) - Complete DSN mode specification
- [DSN Mode P2 Implementation](../DSN_MODE_P2_IMPLEMENTATION.md) - Implementation details
- [DSN Compatibility Analysis](../DSN_COMPATIBILITY_ANALYSIS.md) - Schema analysis
- [Test Helpers](test_helpers.sh) - Shared test utilities
