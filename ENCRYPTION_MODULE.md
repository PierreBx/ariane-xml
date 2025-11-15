# ExpoCLI Encryption Module

## Overview

The ExpoCLI Encryption Module provides comprehensive encryption and pseudonymization capabilities for XML data, specifically designed for French administrative data. It supports:

- **Format-Preserving Encryption (FPE)** for numeric identifiers (NIR, SIREN, SIRET)
- **Faker-based pseudonymization** for French names, addresses, and contact information
- **Date pseudonymization** with age range preservation
- **Reversible encryption** via encrypted mapping tables
- **Password-based security** with PBKDF2 key derivation

## Features

### 1. Format-Preserving Encryption (FPE)

Uses the FF3-1 algorithm to encrypt numeric identifiers while maintaining their format:
- Input: `1234567890123` → Output: `9876543210987`
- Preserves length and numeric format
- Cryptographically secure
- Reversible with the correct password

### 2. French Data Pseudonymization

Generates realistic French data using the Faker library:
- **Names**: French first and last names
- **Addresses**: Complete French addresses
- **Phone numbers**: French phone format
- **Email addresses**: Realistic email patterns
- **Company names**: French company names
- **Postal codes**: Valid French postal codes

### 3. Date Pseudonymization

Modifies dates while preserving age ranges:
- Varies dates by ±N days (configurable)
- Maintains statistical age distribution
- Deterministic (same input → same output)

### 4. Encrypted Mapping Table

All original → encrypted mappings are stored in an encrypted JSON file:
- Encrypted with AES-256-CBC
- Password-based key derivation (PBKDF2)
- Enables full reversibility
- Can be exported for audit purposes

## Installation

### Using Docker (Recommended)

The encryption module is automatically included in the ExpoCLI Docker image:

```bash
docker-compose build
docker-compose up -d
```

### Manual Installation

Install the encryption module:

```bash
pip install -e . -f setup_crypto.py
```

Install dependencies:

```bash
pip install cryptography pyyaml faker lxml ff3
```

## Configuration

Create a YAML configuration file to specify which attributes to encrypt. See `encryption_config.example.yaml` for a complete example.

### Basic Configuration Structure

```yaml
attributes:
  # Encrypt NIR (numeric ID) using FPE
  - pattern: "30.001-30.010"
    type: "fpe"

  # Pseudonymize names using Faker
  - pattern: "06.001"
    type: "faker_name"
    faker_locale: "fr_FR"

  # Pseudonymize dates with ±30 days variance
  - pattern: "11.001"
    type: "date_pseudo"
    date_variance_days: 30

fpe:
  tweak: "expocli"

faker:
  locale: "fr_FR"

mapping_table:
  path: "encryption_mapping.json.enc"
```

### Attribute Pattern Matching

XML attributes follow the pattern: `S10.G00.XX.YYY`

In the configuration, you specify rules using the rightmost two segments:
- **Single attribute**: `"30.001"`
- **Range**: `"30.001-30.010"`

### Encryption Types

| Type | Description | Example |
|------|-------------|---------|
| `fpe` | Format-Preserving Encryption | `1234567890123` → `9876543210987` |
| `faker_name` | French names | `Jean Dupont` → `Marie Martin` |
| `faker_address` | Full French address | Complete address pseudonymization |
| `faker_street` | Street address only | `12 rue de la Paix` → `45 avenue Victor Hugo` |
| `faker_city` | City name | `Paris` → `Lyon` |
| `faker_postal_code` | French postal code | `75001` → `69002` |
| `faker_phone` | French phone number | `01 23 45 67 89` → `04 56 78 90 12` |
| `faker_email` | Email address | Realistic email generation |
| `faker_company` | Company name | French company names |
| `date_pseudo` | Date with variance | `2000-01-15` → `2000-02-10` |

## Usage

### Command-Line Interface

The module provides the `expocli-encrypt` command:

#### 1. Encrypt an XML file

```bash
expocli-encrypt encrypt input.xml encrypted.xml -c config.yaml
```

You will be prompted for a password. This password is used for:
- FPE encryption
- Encrypting the mapping table

#### 2. Decrypt an XML file

```bash
expocli-encrypt decrypt encrypted.xml decrypted.xml -c config.yaml
```

Use the same password and configuration file that was used for encryption.

#### 3. Export mapping table

Export the encrypted mapping table to plaintext JSON for audit:

```bash
expocli-encrypt export-mapping -c config.yaml -o mapping.json
```

#### 4. Show statistics

View mapping table statistics:

```bash
expocli-encrypt stats -c config.yaml
```

### Python API

You can also use the module programmatically:

```python
from expocli_crypto import EncryptionConfig, XMLEncryptor

# Load configuration
config = EncryptionConfig.from_yaml('config.yaml')

# Create encryptor with password
encryptor = XMLEncryptor(config, password='my-secret-password')

# Encrypt file
stats = encryptor.encrypt_file('input.xml', 'encrypted.xml')
print(f"Encrypted {stats['encrypted_attributes']} attributes")

# Decrypt file
stats = encryptor.decrypt_file('encrypted.xml', 'decrypted.xml')
print(f"Decrypted {stats['encrypted_attributes']} attributes")
```

## Example Workflow

### 1. Create configuration file

Copy and customize the example:

```bash
cp encryption_config.example.yaml my_config.yaml
# Edit my_config.yaml to match your needs
```

### 2. Encrypt your data

```bash
expocli-encrypt encrypt data.xml encrypted_data.xml -c my_config.yaml
# Enter password when prompted
```

### 3. Process encrypted data

Your encrypted XML file now contains pseudonymized data. You can:
- Share it for testing
- Use it in development environments
- Perform analytics without exposing real data

### 4. Decrypt when needed

```bash
expocli-encrypt decrypt encrypted_data.xml original_data.xml -c my_config.yaml
# Enter the same password
```

## Security Considerations

### Password Management

- **Use strong passwords**: At least 16 characters, mixed case, numbers, symbols
- **Store securely**: Use a password manager or secure vault
- **Don't commit passwords**: Never commit passwords to version control
- **Separate environments**: Use different passwords for dev/test/prod

### Mapping Table

- **Critical for decryption**: Without the mapping table, Faker-based pseudonymization is NOT reversible
- **Backup regularly**: The mapping table is essential for data recovery
- **Secure storage**: The mapping table is encrypted, but still contains sensitive structure
- **Access control**: Limit who can access the mapping table

### FPE vs Faker

- **FPE**: Mathematically reversible with the correct key
- **Faker**: Reversible ONLY via the mapping table (not mathematically)

### Compliance

This module is designed to help with:
- **GDPR compliance**: Pseudonymization for testing/development
- **Data minimization**: Reducing exposure of personal data
- **Privacy by design**: Built-in encryption capabilities

**Note**: This module provides pseudonymization, not anonymization. The mapping table allows re-identification, which may be required for certain use cases but affects anonymization claims.

## Testing

Create a test script:

```python
# test_encryption.py
from expocli_crypto import EncryptionConfig, XMLEncryptor

# Create simple test configuration
import yaml
config_data = {
    'attributes': [
        {'pattern': '30.001', 'type': 'fpe'},
        {'pattern': '06.001', 'type': 'faker_name'},
    ],
    'mapping_table': {'path': 'test_mapping.json.enc'}
}

with open('test_config.yaml', 'w') as f:
    yaml.dump(config_data, f)

# Test encryption
config = EncryptionConfig.from_yaml('test_config.yaml')
encryptor = XMLEncryptor(config, 'test-password')

# Your test XML file
stats = encryptor.encrypt_file('test_input.xml', 'test_output.xml')
print(stats)
```

## Troubleshooting

### "Could not load mapping table"

- Check that the mapping table file exists
- Verify you're using the correct password
- Ensure the file hasn't been corrupted

### "FPE encryption failed"

- FPE requires minimum 6 digits
- For shorter values, the module automatically falls back to simple substitution
- Check that your numeric IDs meet minimum length requirements

### "No mapping found for attribute"

- The attribute was not in the original encryption run
- You may be using a different configuration file
- Try re-encrypting with the correct configuration

## Architecture

```
expocli_crypto/
├── __init__.py          # Module initialization
├── cli.py               # Command-line interface
├── config.py            # Configuration management (YAML)
├── encryptor.py         # Main XML encryption orchestrator
├── fpe.py               # Format-Preserving Encryption (FF3)
├── pseudonymizer.py     # Faker-based pseudonymization
└── mapping_table.py     # Encrypted mapping table management
```

## Contributing

When adding new encryption types:

1. Add the pseudonymization logic to `pseudonymizer.py`
2. Add the encryption type to `encryptor.py._encrypt_value()`
3. Update the configuration example
4. Add tests
5. Update this documentation

## License

This module is part of the ExpoCLI project.
