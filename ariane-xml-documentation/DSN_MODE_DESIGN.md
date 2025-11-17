# DSN Mode - Design Specification

## Overview
DSN Mode enhances ariane-xml to work seamlessly with French DSN (Déclaration Sociale Nominative) XML files.

## Activation
```sql
SET MODE DSN          -- Enable DSN mode
SHOW MODE             -- Display current mode
SET MODE STANDARD     -- Return to standard mode
```

## Core Features

### 1. **Attribute Shortcuts (YY_ZZZ Notation)**
**Problem:** DSN attributes follow pattern `SWW_GXX_YY_ZZZ` where only YY and ZZZ are meaningful.

**Solution:** Allow users to reference attributes by their meaningful identifiers:

```sql
-- Instead of typing full path:
SELECT S10_G00_00.S10_G00_01.S10_G00_01_001 FROM ./dsn

-- Use shortcut:
SELECT 01_001 FROM ./dsn

-- Or be explicit about ambiguity:
SELECT S10.01_001 FROM ./dsn  -- Specify structure number
```

**Implementation:**
- Parse XSD to build mapping: `(YY, ZZZ) → full_path(s)`
- Detect ambiguous shortcuts (same YY_ZZZ in different structures)
- Provide helpful error messages with suggestions

### 2. **Schema Version Auto-Detection**
```sql
SET DSN_VERSION P25   -- Manually set version
SET DSN_VERSION P26
SET DSN_VERSION AUTO  -- Auto-detect from XML

-- Show current schema info
SHOW DSN_SCHEMA
```

**Auto-detection logic:**
1. Parse root element and version attributes
2. Examine S10_G00_00_006 (version field)
3. Load corresponding P25/P26 schema automatically
4. Validate against correct schema

### 3. **DSN Type Detection**
```sql
-- Auto-detect if file is FCTU, mensuelle, or SADV
SELECT TYPE FROM ./dsn WHERE ...

-- Results include DSN type metadata
File: fctu_2025.xml (Type: FCTU, Version: P25V01)
```

### 4. **Smart Path Completion**
In interactive mode:
```
ariane-xml> SELECT S21_[TAB]
Suggestions:
  S21_G00_06  (ENTREPRISE)
  S21_G00_11  (ETABLISSEMENT)
  S21_G00_30  (INDIVIDU)
  S21_G00_40  (CONTRAT)
  S21_G00_50  (VERSEMENT INDIVIDU)
  ...

ariane-xml> SELECT S21_G00_30.[TAB]
  S21_G00_30_001  NIR - Numéro d'inscription au répertoire
  S21_G00_30_002  Nom de famille
  S21_G00_30_004  Prénoms
  S21_G00_30_006  Date de naissance
  ...
```

### 5. **Field Documentation**
```sql
DESCRIBE 30_001;
-- Output:
-- Rubrique: S21_G00_30_001
-- Bloc: S21.G00.30 (INDIVIDU)
-- Label: NIR - Numéro d'inscription au répertoire
-- Type: Alphanumeric 1-15
-- Mandatory: Optional (0..1)
-- Description: Numéro de sécurité sociale du salarié
-- Versions: P25V01, P26V01

DESCRIBE S21_G00_30;
-- Shows all fields in the INDIVIDU bloc with descriptions
```

### 6. **DSN-Specific Validation**
```sql
CHECK ./dsn/*.xml DSN
-- Additional DSN-specific checks:
-- ✓ Version coherence (P25V01 declaration matches P25 schema)
-- ✓ Mandatory blocs present (ENVOI, DSN_MENSUELLE, etc.)
-- ✓ SIRET format validation (9 digits + 5 digits)
-- ✓ NIR format validation (15 digits with checksum)
-- ✓ Date format consistency (JJMMAAAA)
-- ⚠ Warning: S21_G00_30_001 (NIR) missing but S21_G00_30_020 (temp number) present
```

### 7. **DSN Query Templates**
```sql
-- Predefined useful queries
DSN_TEMPLATE LIST
-- Available templates:
-- - list_employees: List all employees (INDIVIDU)
-- - find_contracts: Find contracts by criteria
-- - extract_salaries: Extract salary information
-- - compliance_check: Basic compliance validation

DSN_TEMPLATE list_employees
-- Executes:
-- SELECT S21_G00_30_002, S21_G00_30_004, S21_G00_30_006
-- FROM ./dsn
-- WHERE S21_G00_30 IS NOT NULL
```

### 8. **Bloc-Level Queries**
```sql
-- Query entire structural blocs
SELECT INDIVIDU.* FROM ./dsn WHERE INDIVIDU.NIR = '123456789012345'

-- Translated internally to:
SELECT S21_G00_30.* FROM ./dsn WHERE S21_G00_30.S21_G00_30_001 = '123456789012345'
```

### 9. **DSN-Aware Formatting**
```sql
-- Output formatted for DSN readability
SELECT * FROM ./dsn LIMIT 1 FORMAT DSN;

-- Output:
╔═════════════════════════════════════════════════════════════════════
║ ENVOI (S10.G00.00)
╠═════════════════════════════════════════════════════════════════════
║ S10_G00_00_001 (Logiciel)          : ARIANE-XML
║ S10_G00_00_002 (Editeur)           : Test Editor
║ S10_G00_00_006 (Version norme)     : P25V01
║
║ EMETTEUR (S10.G00.01)
║ S10_G00_01_001 (SIREN)             : 123456789
║ S10_G00_01_003 (Raison sociale)    : ACME Corporation
╚═════════════════════════════════════════════════════════════════════
```

### 10. **Version Migration Assistance**
```sql
-- Compare schemas between versions
DSN_COMPARE P25 P26;
-- Output:
-- New in P26:
--   + S21_G00_30_315 (nouveau champ)
--   + S21_G00_45_003 (nouveau champ)
-- Modified in P26:
--   ≠ S21_G00_30_007 (optional → mandatory)
-- Deprecated in P26:
--   - S20_G00_08_001 (removed field)

-- Check file compatibility with new version
CHECK ./dsn/fctu_p25.xml UPGRADE_TO P26
-- Lists required changes to migrate to P26
```

## Implementation Architecture

### Phase 1: Foundation
```cpp
// Add to AppContext (app_context.h)
enum class QueryMode {
    STANDARD,
    DSN
};

class AppContext {
    // Existing code...

    // New DSN mode fields
    QueryMode mode_ = QueryMode::STANDARD;
    std::string dsn_version_ = "AUTO";  // P25, P26, or AUTO
    std::optional<DsnSchema> dsn_schema_;  // Parsed DSN XSD

    void setMode(QueryMode mode);
    QueryMode getMode() const;
    void setDsnVersion(const std::string& version);
    std::string getDsnVersion() const;
};
```

### Phase 2: DSN Schema Parser
```cpp
// New: dsn_schema_parser.h
class DsnSchemaParser {
public:
    static DsnSchema parse(const std::string& xsdPath, const std::string& version);

private:
    struct DsnAttribute {
        std::string full_name;      // S21_G00_30_001
        std::string short_id;       // 30_001
        std::string bloc_name;      // S21.G00.30
        std::string description;    // "NIR - Numéro d'inscription..."
        std::string type;           // "Alphanumeric 1-15"
        bool mandatory;
        std::vector<std::string> versions;  // ["P25V01", "P26V01"]
    };

    std::map<std::string, std::vector<DsnAttribute>> shortcut_map_;
    std::map<std::string, DsnAttribute> full_name_map_;
};
```

### Phase 3: Query Rewriting
```cpp
// Modify Parser to rewrite DSN shortcuts
class DsnQueryRewriter {
public:
    Query rewrite(const Query& original, const DsnSchema& schema);

private:
    FieldPath expandShortcut(const std::string& shortcut, const DsnSchema& schema);
    void detectAmbiguity(const std::string& shortcut);
};
```

### Phase 4: Enhanced Output
```cpp
// New formatter: dsn_result_formatter.h
class DsnResultFormatter {
public:
    void format(const std::vector<ResultRow>& results,
                const DsnSchema& schema,
                OutputFormat format);

    enum class OutputFormat {
        TABLE,          // Standard table
        DSN_STRUCTURED, // Hierarchical DSN format
        JSON,           // JSON export
        CSV             // CSV export
    };
};
```

## File Organization

```
ariane-xml-c-kernel/
├── include/
│   ├── dsn/
│   │   ├── dsn_schema.h           # DSN schema representation
│   │   ├── dsn_parser.h           # Parse DSN XSD files
│   │   ├── dsn_query_rewriter.h   # Rewrite shortcuts
│   │   ├── dsn_validator.h        # DSN-specific validation
│   │   └── dsn_formatter.h        # DSN output formatting
│   └── utils/
│       └── app_context.h          # Add QueryMode enum
├── src/
│   ├── dsn/
│   │   ├── dsn_schema.cpp
│   │   ├── dsn_parser.cpp
│   │   ├── dsn_query_rewriter.cpp
│   │   ├── dsn_validator.cpp
│   │   └── dsn_formatter.cpp
│   └── utils/
│       └── command_handler.cpp    # Add "SET MODE DSN" handling
└── ariane-xml-schemas/            # Already exists with XSD files
    ├── xsd_P25/
    └── xsd_P26/
```

## Usage Examples

### Example 1: Basic DSN Query
```sql
-- Standard mode (verbose)
SELECT S21_G00_30.S21_G00_30_002, S21_G00_30.S21_G00_30_006
FROM ./dsn
WHERE S21_G00_30.S21_G00_30_001 = '123456789012345';

-- DSN mode (concise)
SET MODE DSN;
SELECT 30_002, 30_006 FROM ./dsn WHERE 30_001 = '123456789012345';

-- DSN mode (readable aliases)
SELECT nom, date_naissance FROM ./dsn WHERE nir = '123456789012345';
```

### Example 2: Exploring Data
```sql
SET MODE DSN;
DESCRIBE S21_G00_30;  -- See all INDIVIDU fields

SELECT DISTINCT 30_014 FROM ./dsn;  -- All unique birth departments

SELECT COUNT(*) FROM ./dsn WHERE 40_007 = 'CDI';  -- Count CDI contracts
```

### Example 3: Validation
```sql
SET MODE DSN;
SET DSN_VERSION P25;

CHECK ./dsn/*.xml DSN;
-- Performs DSN-specific validation in addition to XSD validation
```

## Migration Path

### For Existing Users:
- **No breaking changes**: Standard mode remains default
- **Opt-in**: DSN mode only activates with `SET MODE DSN`
- **Backward compatible**: All existing queries continue to work

### For DSN Users:
- **Gradual adoption**: Can use standard paths in DSN mode
- **Learning curve**: DESCRIBE commands help discover shortcuts
- **Documentation**: Built-in help for DSN-specific features

## Benefits Summary

| Feature | Standard Mode | DSN Mode |
|---------|--------------|----------|
| DSN file support | ✓ Basic | ✓✓ Optimized |
| Attribute shortcuts | ✗ | ✓ YY_ZZZ notation |
| Schema awareness | ✗ | ✓ P25/P26 detection |
| Field documentation | ✗ | ✓ DESCRIBE command |
| DSN validation | ✗ | ✓ Format checks |
| Auto-completion | ✗ | ✓ Smart suggestions |
| Type detection | ✗ | ✓ FCTU/mensuelle/SADV |
| Hierarchical output | Basic | ✓ DSN-structured |
| Version migration | ✗ | ✓ P25→P26 assistance |
| Templates | ✗ | ✓ Pre-built queries |

## Implementation Priority

**P0 (Essential):**
1. SET MODE DSN command
2. Basic YY_ZZZ shortcut support
3. DSN XSD parser

**P1 (Important):**
4. DESCRIBE command
5. Auto-detection of DSN version
6. DSN-specific validation

**P2 (Nice to have):**
7. Smart auto-completion
8. DSN templates
9. Formatted output
10. Version migration tools

## Estimated Effort

- **P0 Features**: ~2-3 days
- **P1 Features**: ~3-4 days
- **P2 Features**: ~4-5 days
- **Total**: ~10-12 days for full implementation

## Next Steps

1. ✅ Validate DSN XSD schema structure (DONE)
2. ✅ Confirm current app can parse DSN files (DONE)
3. Create DSN schema parser prototype
4. Implement SET MODE DSN command
5. Build shortcut resolution system
6. Add DESCRIBE command
7. Iterate based on user feedback
