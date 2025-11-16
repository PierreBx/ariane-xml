# ExpoCLI Documentation Index

Complete documentation for ExpoCLI - SQL-like query tool for XML files with encryption.

## Quick Start Guides (Start Here!)

Get up and running in 5 minutes:

- **[01a - CLI Quick Start](01a_Quick_Start_CLI.md)** - Command-line interface basics
- **[01b - Jupyter Quick Start](01b_Quick_Start_Jupyter.md)** - Notebook interface basics
- **[01c - Encryption Quick Start](01c_Quick_Start_Encryption.md)** - XML encryption basics

## Installation & Setup

- **[02 - Installation Guide](02_Installation_Guide.md)** - Complete installation instructions
  - Docker installation
  - Local build instructions
  - Troubleshooting

## Core Features

### Jupyter Integration

- **[04 - Jupyter Integration](04_Jupyter_Integration.md)** - Full Jupyter documentation
- **[04b - Jupyter Technical Analysis](04b_Jupyter_Technical_Analysis.md)** - Technical implementation details
- **[04c - Jupyter POC Summary](04c_Jupyter_POC_Summary.md)** - Proof of concept summary
- **[04d - Jupyter Enhancements](04d_Jupyter_Enhancements.md)** - Enhancement proposals
- **[04e - Testing Enhanced Kernel](04e_Testing_Enhanced_Kernel.md)** - Kernel testing guide

### XML Encryption

- **[06 - Encryption Quick Start](06_Encryption_Quick_Start.md)** - 5-minute encryption guide
- **[07 - Encryption Module](07_Encryption_Module.md)** - Complete encryption reference
- **[07b - Encryption Implementation](07b_Encryption_Implementation.md)** - Technical architecture
- **[07c - Encryption Setup](07c_Encryption_Setup.md)** - Setup and configuration

## Docker & DevOps

- **[08 - Docker Rebuild Guide](08_Docker_Rebuild_Guide.md)** - How to rebuild after changes
- **[08b - Docker Proxy Fix](08b_Docker_Proxy_Fix.md)** - Fixing Docker proxy issues
- **[13 - Docker Buildx Setup](13_Docker_Buildx_Setup.md)** - Installing Buildx for faster builds

## Reference

- **[09 - Known Issues](09_Known_Issues.md)** - Troubleshooting guide
- **[10 - Architecture Diagram](10_Architecture_Diagram.md)** - System architecture
- **[11 - Performance Analysis](11_Performance_Analysis.md)** - Performance benchmarks

## Documentation by Topic

### For New Users
1. [CLI Quick Start](01a_Quick_Start_CLI.md)
2. [Installation Guide](02_Installation_Guide.md)
3. [Known Issues](09_Known_Issues.md)

### For Jupyter Users
1. [Jupyter Quick Start](01b_Quick_Start_Jupyter.md)
2. [Jupyter Integration](04_Jupyter_Integration.md)
3. [Jupyter Technical Analysis](04b_Jupyter_Technical_Analysis.md)

### For Data Protection
1. [Encryption Quick Start](01c_Quick_Start_Encryption.md)
2. [Encryption Module](07_Encryption_Module.md)
3. [Encryption Setup](07c_Encryption_Setup.md)

### For Developers
1. [Architecture Diagram](10_Architecture_Diagram.md)
2. [Performance Analysis](11_Performance_Analysis.md)
3. [Encryption Implementation](07b_Encryption_Implementation.md)

### For DevOps
1. [Installation Guide](02_Installation_Guide.md)
2. [Docker Rebuild Guide](08_Docker_Rebuild_Guide.md)
3. [Docker Proxy Fix](08b_Docker_Proxy_Fix.md)

## Quick Reference

### Query Syntax

```sql
SELECT <field>[,<field>...]
FROM <path>
[WHERE <condition>]
[ORDER BY <field>]
[LIMIT n]
```

### Common Commands

```bash
# CLI
expocli                                # Interactive mode
expocli "SELECT name FROM ./data"      # Single query

# Jupyter
docker compose up -d jupyter           # Start Jupyter
# Open http://localhost:8888

# Encryption
expocli-encrypt encrypt in.xml out.xml -c config.yaml
expocli-encrypt decrypt enc.xml dec.xml -c config.yaml
```

### File Locations

- **Examples**: `examples/`
- **Tests**: `tests/`
- **Configuration**: `config/encryption_config.example.yaml`
- **Build**: `build/`
- **Source**: `src/`

## Getting Help

1. **Check Quick Starts** - Most common questions answered
2. **See Known Issues** - Common problems and solutions
3. **Read Detailed Docs** - In-depth information
4. **Check Examples** - Sample code and data

## Contributing

See the main [README](../README.md) for:
- Project structure
- Development setup
- Testing guidelines
- Code architecture

---

**Quick Links:**
- [← Back to Main README](../README.md)
- [CLI Quick Start →](01a_Quick_Start_CLI.md)
- [Jupyter Quick Start →](01b_Quick_Start_Jupyter.md)
- [Encryption Quick Start →](01c_Quick_Start_Encryption.md)
