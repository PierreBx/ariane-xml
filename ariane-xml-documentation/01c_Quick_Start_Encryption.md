# Ariane-XML Quick Start - XML Encryption

Get started with encrypting and pseudonymizing XML data in 5 minutes.

## What is ariane-xml-encrypt?

A powerful encryption tool for XML files with:
- 🔐 **Format-Preserving Encryption** for numeric IDs (NIR, SIREN, SIRET)
- 🇫🇷 **French pseudonymization** for names, addresses, phone numbers
- 📅 **Date pseudonymization** with age range preservation
- 🔄 **Full reversibility** via encrypted mapping tables
- 🔑 **Password-based encryption** with industry-standard security

## Installation

### Using Docker (Recommended)

The encryption module is already installed in the Docker container:

```bash
# Start container
docker compose up -d ariane-xml

# Test installation
docker compose exec ariane-xml ariane-xml-encrypt --help
```

**Note:** If you see "command not found", you may need to rebuild after fixing the Docker proxy issue. See [Docker Rebuild Guide](08_Docker_Rebuild_Guide.md).

### Manual Installation

```bash
# Install dependencies
./install_crypto.sh

# Verify
ariane-xml-encrypt --help
```

## Quick Example

### 1. Copy Example Configuration

```bash
cp config/encryption_config.example.yaml my_config.yaml
```

### 2. Encrypt a File

```bash
# Inside Docker
docker compose exec ariane-xml bash -c "cd /app/tests/encryption && \
  ariane-xml-encrypt encrypt sample_data.xml encrypted.xml -c ../../config/encryption_config.example.yaml"

# You'll be prompted for a password
Enter encryption password: ****
```

Output:
```
Encryption completed successfully!
Total attributes: 19
Encrypted attributes: 19

By encryption type:
  fpe: 5
  faker_name: 4
  faker_street: 2
  faker_city: 2
  ...
```

### 3. View Encrypted Data

```bash
cat encrypted.xml
```

You'll see:
- **NIR**: `1234567890123` → `9282107946190` (same format!)
- **Names**: `Jean Dupont` → `Gérard Delorme` (French names)
- **Addresses**: `Paris` → `Allard` (French cities)
- **Dates**: `2000-01-15` → `2000-02-04` (±30 days)

### 4. Decrypt Back to Original

```bash
ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c my_config.yaml
# Use the same password!
```

### 5. Verify

```bash
diff sample_data.xml decrypted.xml
# Only XML declaration format differs - data is identical!
```

## Configuration

Edit `my_config.yaml` to specify which attributes to encrypt:

```yaml
attributes:
  # NIR (Format-Preserving Encryption)
  - pattern: "30.001-30.010"
    type: "fpe"

  # Names (French pseudonymization)
  - pattern: "06.001"
    type: "faker_name"
    faker_locale: "fr_FR"

  # Dates (with variance)
  - pattern: "11.001"
    type: "date_pseudo"
    date_variance_days: 30
```

### Pattern Matching

XML elements like `<S21.G00.30.001>` match pattern `"30.001"` (last two segments).

Use ranges: `"30.001-30.010"` matches 30.001 through 30.010.

## Encryption Types

| Type | Description | Example |
|------|-------------|---------|
| `fpe` | Format-Preserving Encryption | `123456789` → `987654321` |
| `faker_name` | French names | `Jean Dupont` → `Marie Martin` |
| `faker_address` | Full addresses | Complete address replacement |
| `faker_street` | Street only | `12 rue de la Paix` → `45 av Victor Hugo` |
| `faker_city` | City names | `Paris` → `Lyon` |
| `faker_postal_code` | Postal codes | `75001` → `69002` |
| `faker_phone` | Phone numbers | `01 23 45 67 89` → `04 56 78 90 12` |
| `faker_email` | Emails | Generated French emails |
| `faker_company` | Company names | French company names |
| `date_pseudo` | Date with variance | `2000-01-15` → `2000-02-10` |

## Common Use Cases

### Use Case 1: Anonymize for Testing

```bash
# Encrypt production data for testing
ariane-xml-encrypt encrypt prod_data.xml test_data.xml -c config.yaml

# Share test_data.xml with testers (safely!)
# Keep encryption_mapping.json.enc secure for reversal
```

### Use Case 2: GDPR Compliance

```yaml
# Configure to pseudonymize personal data only
attributes:
  - pattern: "30.001"  # NIR
    type: "fpe"
  - pattern: "06.001"  # Name
    type: "faker_name"
  - pattern: "11.001"  # Birth date
    type: "date_pseudo"
```

### Use Case 3: Selective Encryption

```yaml
# Encrypt only specific sensitive fields
attributes:
  - pattern: "30.001"  # Just NIR
    type: "fpe"
```

## CLI Commands

### Encrypt

```bash
ariane-xml-encrypt encrypt input.xml output.xml -c config.yaml [-p password]
```

### Decrypt

```bash
ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c config.yaml [-p password]
```

### View Statistics

```bash
ariane-xml-encrypt stats -c config.yaml [-p password]
```

Output:
```
Mapping Table Statistics
Total categories: 10
Total entries: 152

By category:
  S21.G00.30.001:fpe: 15 entries
  S21.G00.06.001:faker_name: 28 entries
  ...
```

### Export Mapping

```bash
ariane-xml-encrypt export-mapping -c config.yaml -o mapping.json
```

Creates a plaintext JSON file for audit purposes.

## Security Best Practices

### Password Management

- ✅ Use strong passwords (16+ characters)
- ✅ Store in password manager
- ✅ Different passwords for dev/test/prod
- ❌ Never commit passwords to git

### Mapping Table

- ✅ Backup `encryption_mapping.json.enc` securely
- ✅ Required for decryption
- ✅ Encrypted with AES-256-CBC
- ⚠️ Control access carefully

### Configuration

- ✅ Store `config.yaml` in version control
- ✅ Document what gets encrypted
- ❌ Never store passwords in config

## Tips

1. **Test first** with sample data
2. **Backup** original files before encrypting
3. **Keep mapping table** for reversibility
4. **Document** your encryption config
5. **Use version control** for config files

## Troubleshooting

### "ariane-xml-encrypt: command not found"

See [Encryption Setup Guide](07c_Encryption_Setup.md) for installation.

### "Could not load mapping table"

- Check password is correct
- Verify file path in config
- Ensure file isn't corrupted

### "FPE encryption failed"

FPE requires minimum 6 digits. For shorter IDs, module uses simple substitution (still reversible).

## Next Steps

- 📖 Full [Encryption Module Documentation](07_Encryption_Module.md)
- 🔧 [Setup Guide](07c_Encryption_Setup.md) for installation details
- 🏗️ [Implementation Details](07b_Encryption_Implementation.md) for architecture
- 🐳 [Docker Rebuild](08_Docker_Rebuild_Guide.md) if needed

## Example Workflow

```bash
# 1. Configure
cp config/encryption_config.example.yaml my_config.yaml
nano my_config.yaml

# 2. Test with sample
cd tests/encryption
ariane-xml-encrypt encrypt sample_data.xml test.xml -c ../../my_config.yaml

# 3. Verify
head test.xml

# 4. Decrypt to verify reversibility
ariane-xml-encrypt decrypt test.xml check.xml -c ../../my_config.yaml
diff sample_data.xml check.xml

# 5. Use with real data
ariane-xml-encrypt encrypt ../prod_data.xml ../encrypted_prod.xml -c ../../my_config.yaml

# 6. Backup mapping table
cp encryption_mapping.json.enc ../../backups/
```

Ready to encrypt your data securely! 🔐
