# Ariane-XML Encryption Module - Quick Start Guide

## 5-Minute Quick Start

### 1. Installation

#### Using Docker (Easiest)

```bash
# Build the Docker image (includes encryption module)
docker-compose build

# Start container
docker-compose up -d

# Enter container
docker-compose exec ariane-xml bash

# Verify installation
ariane-xml-encrypt --help
```

#### Manual Installation

```bash
# Run installation script
./install_crypto.sh

# Or install manually
pip3 install cryptography pyyaml faker lxml ff3
pip3 install -e . -f setup_crypto.py
```

### 2. Create Configuration

Copy the example configuration:

```bash
cp config/encryption_config.example.yaml my_config.yaml
```

The example configuration is pre-configured for the attributes you specified:
- `30.001-30.010`: NIR (FPE encryption)
- `40.001-40.010`: SIREN/SIRET (FPE encryption)
- `06.001-06.010`: Names and addresses (Faker pseudonymization)
- `11.001-11.005`: Various personal data

### 3. Encrypt Your First File

```bash
# Encrypt
ariane-xml-encrypt encrypt input.xml encrypted.xml -c my_config.yaml

# You'll be prompted for a password - remember it!
# Enter encryption password: ********
```

**Important**: Store your password securely! You'll need it to decrypt.

### 4. View Results

```bash
# View statistics
ariane-xml-encrypt stats -c my_config.yaml

# Export mapping table (for verification)
ariane-xml-encrypt export-mapping -c my_config.yaml -o mapping.json
cat mapping.json
```

### 5. Decrypt

```bash
# Decrypt back to original
ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c my_config.yaml

# Enter the same password
# Enter encryption password: ********
```

## Example with Sample Data

We've included sample data for testing:

```bash
cd tests/encryption

# Encrypt the sample data
ariane-xml-encrypt encrypt sample_data.xml encrypted_sample.xml -c ../../config/encryption_config.example.yaml

# View the encrypted file
cat encrypted_sample.xml

# Decrypt it
ariane-xml-encrypt decrypt encrypted_sample.xml decrypted_sample.xml -c ../../config/encryption_config.example.yaml

# Compare
diff sample_data.xml decrypted_sample.xml
# Should show no differences!
```

## Customizing Configuration

Edit `my_config.yaml` to match your specific attributes:

```yaml
attributes:
  # Add your specific attributes
  - pattern: "30.001-30.010"  # NIR range
    type: "fpe"               # Format-preserving encryption

  - pattern: "06.001"         # Single attribute
    type: "faker_name"        # French names

  # Dates with age preservation
  - pattern: "11.001"
    type: "date_pseudo"
    date_variance_days: 30    # ±30 days
```

## Understanding the Encryption Types

| Your Data Type | Encryption Type | Example |
|----------------|-----------------|---------|
| NIR, SIREN, SIRET | `fpe` | `1234567890123` → `9876543210987` |
| Person names | `faker_name` | `Jean Dupont` → `Marie Martin` |
| Street addresses | `faker_street` | `12 rue de la Paix` → `45 av Victor Hugo` |
| City names | `faker_city` | `Paris` → `Lyon` |
| Postal codes | `faker_postal_code` | `75001` → `69002` |
| Birth dates | `date_pseudo` | `2000-01-15` → `2000-02-10` (±30d) |
| Phone numbers | `faker_phone` | `01 23 45 67 89` → `04 56 78 90 12` |
| Emails | `faker_email` | Auto-generated French emails |
| Company names | `faker_company` | French company names |

## Running Tests

```bash
# Run encryption module tests
python3 -m pytest tests/encryption/test_encryption.py -v

# Or with unittest
python3 -m unittest tests/encryption/test_encryption.py
```

## Common Use Cases

### Use Case 1: Encrypt for Testing Environment

```bash
# Encrypt production data for testing
ariane-xml-encrypt encrypt prod_data.xml test_data.xml -c config.yaml

# Share test_data.xml with testers
# Keep encryption_mapping.json.enc secure for reversal if needed
```

### Use Case 2: Selective Encryption

Edit config to encrypt only specific attributes:

```yaml
attributes:
  # Only encrypt NIR
  - pattern: "30.001"
    type: "fpe"
```

### Use Case 3: Multiple Environments

```bash
# Use different passwords for different environments
ariane-xml-encrypt encrypt data.xml dev_data.xml -c config.yaml -p dev-password
ariane-xml-encrypt encrypt data.xml test_data.xml -c config.yaml -p test-password
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ariane-xml_crypto'"

**Solution**: Install the module:
```bash
pip3 install -e . -f setup_crypto.py
```

### Issue: "Could not load mapping table"

**Solution**: Check password and file path:
```bash
# Verify the mapping file exists
ls -l encryption_mapping.json.enc

# Try with correct password
ariane-xml-encrypt stats -c config.yaml
```

### Issue: "FPE encryption failed"

**Solution**: FPE requires minimum 6 digits. For shorter IDs, the module falls back to simple substitution (still reversible).

### Issue: Values not being encrypted

**Solution**: Check your attribute patterns in config.yaml:
```bash
# The pattern matches the LAST TWO segments of the attribute name
# For S21.G00.30.001, use pattern "30.001"
```

## Security Best Practices

1. **Password Management**
   - Use strong passwords (16+ characters)
   - Don't commit passwords to git
   - Use different passwords for dev/test/prod

2. **Mapping Table**
   - Backup `encryption_mapping.json.enc` securely
   - This file is required for decryption
   - It's encrypted, but still control access

3. **Configuration**
   - Store `config.yaml` in version control
   - Never store passwords in config files
   - Use environment variables for sensitive data

4. **File Permissions**
   ```bash
   # Secure the mapping table
   chmod 600 encryption_mapping.json.enc
   ```

## Next Steps

- Read [ENCRYPTION_MODULE.md](ENCRYPTION_MODULE.md) for full documentation
- Customize `my_config.yaml` for your specific needs
- Integrate into your CI/CD pipeline
- Set up automated backups of mapping tables

## Need Help?

- Check the full documentation: `ENCRYPTION_MODULE.md`
- Run tests to verify installation: `python3 -m pytest tests/encryption/`
- View CLI help: `ariane-xml-encrypt --help`
- View command-specific help: `ariane-xml-encrypt encrypt --help`
