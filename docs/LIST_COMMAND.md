# LIST Command Documentation

## Overview

The `LIST` command provides a convenient way to inspect all XML files in a directory, displaying comprehensive information about each file including its nature (DSN or STANDARD), size, version, validation status, and encryption state.

## Syntax

```sql
LIST <directory_path>
```

### Parameters

- `<directory_path>` (required): Unix-like path to the directory containing XML files
  - Can be absolute: `/home/user/data`
  - Can be relative: `./data` or `../samples`
  - Quotes are optional for most paths: `LIST ./ariane-xml-tests/data`
  - Use quotes if the path contains spaces: `LIST "/path/with spaces"`

## Output

The LIST command displays a table with the following columns:

| Column | Description | Applies To |
|--------|-------------|------------|
| **Filename** | Name of the XML file | All files |
| **Size** | File size in human-readable format (B, KB, MB, GB) | All files |
| **Nature** | File type: `DSN` or `STANDARD` | All files |
| **Version** | DSN version (e.g., `P25`, `P26`) | DSN files only |
| **Valid** | XSD validation status (`Valid`, `Invalid`, or `-` if not validated) | DSN files only |
| **Encrypted** | Encryption/pseudonymization status (`Yes`, `No`) | DSN files only |

### Nature Detection

A file is classified as **DSN** if its root XML element matches one of the configured DSN root elements:
- `DSN_FCTU_HY` - DSN Flow Type HY (Hybrid)
- `DSN_FCTU_M` - DSN Flow Type M (Monthly)
- `DSN_FCTU` - DSN Flow Type (Generic)
- `DSN_SITU` - DSN Situation Report
- `DSN_ANNUL` - DSN Cancellation
- `DSN_RETRAIT` - DSN Withdrawal

The list of DSN root elements can be configured in `ariane-xml-config/dsn_detection.yml`.

### Version Detection

For DSN files, the version is automatically detected from the file content by looking for the version indicator element (typically `S10_G00_00_006`), which contains values like `P25V01` or `P26V02`. The command extracts the phase (P25, P26, etc.) from this value.

### Encryption Detection

The command checks for the presence of the `<?ariane-pseudonymised?>` processing instruction in the XML file. If present, the file is marked as encrypted/pseudonymized.

### Validation Status

**Note:** Validation is currently not performed until XSD schema files are provided. The validation column will show `-` until schemas are configured.

Once XSD files are available in `ariane-xml-config/xsd/`:
- DSN files will be validated against their corresponding schema (P25 → `P25_schema.xsd`, P26 → `P26_schema.xsd`)
- Valid files will show `Valid`
- Invalid files will show `Invalid`
- STANDARD files will not be validated

## Examples

### List files in current directory

```sql
LIST .
```

### List files in absolute path

```sql
LIST /home/user/ariane-xml/ariane-xml-tests/data
```

### List files in relative path

```sql
LIST ./data
```

### List files with path containing spaces (quotes required)

```sql
LIST "/path/with spaces/data"
```

### Example Output

```
Filename               Size      Nature      Version   Valid       Encrypted
----------------------- --------- ----------- --------- ----------- -----------
books1.xml             499 B     STANDARD    -         -           -
books2.xml             692 B     STANDARD    -         -           -
company.xml            1.3 KB    STANDARD    -         -           -
test_dsn_sample.xml    1.9 KB    DSN         P25       -           No

Total: 4 XML file(s)
```

## Error Codes

The LIST command uses the unified ARX error numbering system:

| Error Code | Severity | Description |
|------------|----------|-------------|
| `ARX-00000` | Success | Normal completion - directory accessed successfully, no XML files found (no errors) |
| `ARX-20010` | Error | Directory not found |
| `ARX-20011` | Error | Permission denied accessing directory |
| `ARX-20012` | Error | Invalid directory path |
| `ARX-20013` | Error | Failed to read directory contents |

### Error Examples

```bash
# Directory not found
$ ariane-xml 'LIST "/nonexistent/path"'
ARX-20010 [Error] Directory not found: /nonexistent/path

# No XML files (normal completion)
$ ariane-xml 'LIST "/empty/directory"'
No XML files found in directory: /empty/directory
ARX-00000 [Success]
```

## Configuration

### DSN Detection Configuration

The DSN root elements are configured in `ariane-xml-config/dsn_detection.yml`:

```yaml
# DSN Detection Configuration
dsn_root_elements:
  - DSN_FCTU_HY      # DSN Flow Type HY (Hybrid)
  - DSN_FCTU_M       # DSN Flow Type M (Monthly)
  - DSN_FCTU         # DSN Flow Type (Generic)
  - DSN_SITU         # DSN Situation Report
  - DSN_ANNUL        # DSN Cancellation
  - DSN_RETRAIT      # DSN Withdrawal

version_xpath: "//S10_G00_00/S10_G00_00_006"

version_patterns:
  - pattern: "^P25V\\d{2}$"
    version: "P25"
    description: "DSN Phase 25"

  - pattern: "^P26V\\d{2}$"
    version: "P26"
    description: "DSN Phase 26"

xsd_mapping:
  P25: "P25_schema.xsd"
  P26: "P26_schema.xsd"
```

## Use Cases

### 1. Quick Directory Inventory

Quickly see what XML files are in a directory and their basic properties:

```sql
LIST "./samples"
```

### 2. DSN File Identification

Identify which files in a directory are DSN files vs standard XML files:

```sql
LIST "/data/mixed"
```

### 3. Version Checking

Check which DSN version (P25, P26) your files are using:

```sql
LIST "./dsn_files"
```

### 4. Encryption Audit

Verify which files have been encrypted/pseudonymized:

```sql
LIST "./sensitive_data"
```

## Notes

- The LIST command only scans files with `.xml` extension (case-insensitive)
- Subdirectories are not recursively scanned
- Files that cannot be parsed (malformed XML) are skipped without error
- The command returns immediately after listing files; it does not load or process the file contents
- File sizes are displayed in the most appropriate unit (B, KB, MB, GB)

## See Also

- [CHECK Command](CHECK_COMMAND.md) - Validate XML files against XSD schema
- [PSEUDONYMISE Command](PSEUDONYMISE_COMMAND.md) - Encrypt/pseudonymize DSN files
- [Error Codes Reference](../error_catalog.yaml) - Complete error code catalog
- [DSN Detection Configuration](../ariane-xml-config/dsn_detection.yml) - Configure DSN file detection
