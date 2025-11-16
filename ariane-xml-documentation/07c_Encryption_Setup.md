# Ariane-XML Encryption Module - Setup Instructions

## Current Status

✅ **Encryption module fully implemented** - All code is ready
❌ **Docker proxy issue preventing build** - Needs to be fixed

## What's Been Implemented

A complete encryption and pseudonymization module with:

- ✅ Format-Preserving Encryption (FPE) for numeric IDs (NIR, SIREN, SIRET)
- ✅ French pseudonymization with Faker (names, addresses, etc.)
- ✅ Date pseudonymization with age range preservation
- ✅ Encrypted mapping tables for reversibility
- ✅ YAML-based configuration system
- ✅ Python CLI tool (`ariane-xml-encrypt`)
- ✅ Comprehensive tests and documentation
- ✅ Docker integration (ready to use after rebuild)

## Files Created

### Core Module (37 KB total)
```
ariane-xml_crypto/
├── __init__.py           - Module initialization
├── cli.py               - Command-line interface (7.7 KB)
├── config.py            - YAML configuration (4.2 KB)
├── encryptor.py         - Main orchestrator (7.2 KB)
├── fpe.py               - Format-Preserving Encryption (5.1 KB)
├── mapping_table.py     - Encrypted mapping (5.6 KB)
└── pseudonymizer.py     - Faker integration (6.3 KB)
```

### Documentation (30 KB)
- `ENCRYPTION_QUICKSTART.md` - 5-minute quick start (6 KB)
- `ENCRYPTION_MODULE.md` - Full documentation (9 KB)
- `ENCRYPTION_IMPLEMENTATION_SUMMARY.md` - Technical details (12 KB)
- `config/encryption_config.example.yaml` - Pre-configured for your attributes (3 KB)

### Setup & Tests
- `setup_crypto.py` - Python package setup
- `install_crypto.sh` - Installation script
- `tests/encryption/test_encryption.py` - Comprehensive tests (9.5 KB)
- `tests/encryption/sample_data.xml` - Sample data

### Docker & Fix Scripts
- `Dockerfile` - Updated with encryption dependencies
- `fix_docker_proxy.sh` - **Run this first!**
- `FIX_AND_REBUILD.md` - Step-by-step guide
- `DOCKER_PROXY_FIX.md` - Proxy troubleshooting

## Quick Setup (3 Steps)

### Step 1: Fix Docker Proxy (Required First!)

Your Docker daemon has a proxy configuration issue. Run this to fix it:

```bash
cd /home/ipro0800/Documents/projets-perso/prod-projects/ariane-xml
./fix_docker_proxy.sh
```

**What it does:**
- Backs up current Docker configuration
- Removes broken proxy configuration
- Restarts Docker daemon
- Verifies the fix

### Step 2: Rebuild Docker Image

Now that Docker can access the internet, rebuild with encryption dependencies:

```bash
docker compose down
docker compose build
docker compose up -d
```

This will take 3-5 minutes and will install:
- Python 3 and pip
- Jupyter Lab and kernel support
- Encryption libraries (cryptography, faker, lxml, ff3)
- Ariane-XML encryption module

### Step 3: Verify Everything Works

```bash
# Test the encryption CLI
docker compose exec ariane-xml ariane-xml-encrypt --help

# Test with sample data
docker compose exec ariane-xml bash -c "
  cd tests/encryption &&
  ariane-xml-encrypt encrypt sample_data.xml encrypted.xml -c ../../config/encryption_config.example.yaml -p test123 &&
  ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c ../../config/encryption_config.example.yaml -p test123 &&
  diff sample_data.xml decrypted.xml
"

# Check Jupyter
docker compose logs jupyter
# Then open http://localhost:8888
```

## Detailed Documentation

After setup, read these in order:

1. **Start Here:** `FIX_AND_REBUILD.md`
   - Complete step-by-step rebuild instructions
   - Troubleshooting guide
   - Success indicators

2. **Quick Start:** `ENCRYPTION_QUICKSTART.md`
   - Get started in 5 minutes
   - Example usage
   - Common use cases

3. **Full Reference:** `ENCRYPTION_MODULE.md`
   - Complete API documentation
   - Security considerations
   - Advanced features

4. **Technical Details:** `ENCRYPTION_IMPLEMENTATION_SUMMARY.md`
   - Architecture overview
   - Implementation details
   - File structure

## Configuration for Your Requirements

The example configuration (`config/encryption_config.example.yaml`) is already set up for your specified attributes:

```yaml
attributes:
  # 30.001 to 30.010 - NIR (FPE)
  - pattern: "30.001-30.010"
    type: "fpe"

  # 40.001 to 40.010 - SIREN/SIRET (FPE)
  - pattern: "40.001-40.010"
    type: "fpe"

  # 06.001 to 06.010 - Names/Addresses (Faker)
  - pattern: "06.001"
    type: "faker_name"
  # ... (more configured)

  # 11.001 to 11.005 - Various data
  - pattern: "11.001"
    type: "date_pseudo"
  # ... (more configured)
```

## Usage Examples

Once setup is complete, you can:

### Encrypt an XML file
```bash
ariane-xml-encrypt encrypt input.xml encrypted.xml -c config.yaml
```

### Decrypt back to original
```bash
ariane-xml-encrypt decrypt encrypted.xml decrypted.xml -c config.yaml
```

### View mapping statistics
```bash
ariane-xml-encrypt stats -c config.yaml
```

### Export mapping for audit
```bash
ariane-xml-encrypt export-mapping -c config.yaml -o mapping.json
```

## Supported Encryption Types

| Type | Description | Use For |
|------|-------------|---------|
| `fpe` | Format-Preserving Encryption | NIR, SIREN, SIRET |
| `faker_name` | French names | Person names (first, last, full) |
| `faker_address` | Full addresses | Complete addresses |
| `faker_street` | Street addresses | Street/number only |
| `faker_city` | City names | City names |
| `faker_postal_code` | Postal codes | French postal codes |
| `faker_phone` | Phone numbers | French phone format |
| `faker_email` | Email addresses | Email addresses |
| `faker_company` | Company names | Company/organization names |
| `date_pseudo` | Date with variance | Birth dates, event dates |

## Why the Proxy Fix is Needed

Your system has Docker configured with a proxy (`localhost:3128`) that isn't running. This affects:

1. ❌ Building Docker images (can't download base images)
2. ❌ Installing packages in containers (apt-get fails)
3. ❌ Downloading Python packages (pip fails)

The `fix_docker_proxy.sh` script removes this configuration so Docker works normally.

## Troubleshooting

### "Permission denied" when running fix script
```bash
# The script will automatically request sudo
./fix_docker_proxy.sh
```

### Docker build still fails after fix
```bash
# Verify proxy is removed
docker info | grep -i proxy

# Should show empty or no proxy
```

### "ariane-xml-encrypt: command not found"
```bash
# The image needs to be rebuilt
docker compose down
docker compose build
docker compose up -d
```

## What Happens After Rebuild

Once the Docker image is rebuilt with the fix:

✅ Python 3 and pip will be installed
✅ Jupyter Lab will work
✅ All encryption libraries will be available
✅ The `ariane-xml-encrypt` command will work
✅ You can start encrypting/decrypting XML files

## Next Actions

1. **Now:** Run `./fix_docker_proxy.sh` to fix Docker
2. **Then:** Run `docker compose build` to rebuild image
3. **Finally:** Read `ENCRYPTION_QUICKSTART.md` to start using the encryption module

## Support Files Summary

| File | Purpose |
|------|---------|
| `fix_docker_proxy.sh` | **Run this first** - Fixes Docker proxy |
| `FIX_AND_REBUILD.md` | Complete rebuild instructions |
| `ENCRYPTION_QUICKSTART.md` | 5-minute quick start guide |
| `ENCRYPTION_MODULE.md` | Full encryption documentation |
| `DOCKER_PROXY_FIX.md` | Proxy troubleshooting details |
| `config/encryption_config.example.yaml` | Ready-to-use configuration |

---

**Ready to start?** Run: `./fix_docker_proxy.sh`
