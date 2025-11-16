# ExpoCLI

A high-performance SQL-like query tool for XML files with encryption capabilities.

## Features

- 🔍 **SQL-like Query Syntax** - Familiar SELECT/FROM/WHERE/ORDER BY/LIMIT syntax
- 🚀 **Interactive & Batch Modes** - REPL interface or single-query execution
- 📊 **Jupyter Integration** - Run queries in notebooks for data exploration
- 🔐 **XML Encryption** - Format-preserving encryption and French data pseudonymization
- ⚡ **High Performance** - Built with C++17 and pugixml
- 🐳 **Docker Support** - Consistent environment, works anywhere

## Quick Start

### Installation

```bash
# Clone and install (creates transparent local command)
git clone <repository-url>
cd expocli
./install.sh

# Reload shell
source ~/.bashrc
```

### Run a Query

```bash
# Interactive mode
expocli

# Single query
expocli "SELECT name FROM ./data WHERE price < 30"
```

### Example Queries

```sql
-- Simple query
SELECT breakfast_menu/food/name FROM ./examples

-- With conditions
SELECT name, price FROM ./examples WHERE price < 10

-- Multiple files with ordering
SELECT FILE_NAME, name FROM ./data WHERE calories < 500 ORDER BY price LIMIT 10

-- Complex conditions
SELECT name FROM ./data WHERE (price < 50 AND calories < 1000) OR rating > 4
```

## Documentation

### Quick Start Guides (5 minutes each)

- 📘 [CLI Quick Start](expocli_documentation/01a_Quick_Start_CLI.md) - Command-line interface
- 📙 [Jupyter Quick Start](expocli_documentation/01b_Quick_Start_Jupyter.md) - Notebook interface
- 📗 [Encryption Quick Start](expocli_documentation/01c_Quick_Start_Encryption.md) - XML encryption

### Detailed Documentation

- [Installation Guide](expocli_documentation/02_Installation_Guide.md) - Complete installation instructions
- [Jupyter Integration](expocli_documentation/04_Jupyter_Integration.md) - Full Jupyter documentation
- [Encryption Module](expocli_documentation/07_Encryption_Module.md) - Complete encryption reference
- [Known Issues](expocli_documentation/09_Known_Issues.md) - Troubleshooting guide
- [Architecture](expocli_documentation/10_Architecture_Diagram.md) - System architecture

## Main Components

### 1. ExpoCLI (Query Engine)

Query XML files using SQL-like syntax:

```bash
expocli "SELECT name, price FROM ./data WHERE price < 50"
```

**Features:**
- Interactive REPL with command history
- Single-query batch mode
- Multi-file queries
- Complex WHERE conditions with AND/OR/parentheses
- ORDER BY and LIMIT support

### 2. Jupyter Integration

Run queries in Jupyter notebooks:

```sql
-- In a Jupyter cell
SELECT name FROM /app/examples WHERE calories < 600
```

**Features:**
- Cell-based execution
- Persistent results
- Mix queries with documentation
- Export to PDF/HTML

### 3. XML Encryption (expocli-encrypt)

Encrypt and pseudonymize XML data:

```bash
expocli-encrypt encrypt input.xml encrypted.xml -c config.yaml
```

**Features:**
- Format-Preserving Encryption (NIR, SIREN, SIRET)
- French data pseudonymization (names, addresses)
- Date pseudonymization with age preservation
- Full reversibility via encrypted mapping tables
- YAML-based configuration

## Query Syntax

```sql
SELECT <field>[,<field>...]
FROM <path>
[WHERE <condition>]
[ORDER BY <field> [ASC|DESC]]
[LIMIT n]
```

**Field Paths:** Use dot or slash notation
- `breakfast_menu.food.name`
- `breakfast_menu/food/name`

**Special Fields:**
- `FILE_NAME` - Include source filename in results

**Operators:** `=`, `!=`, `<`, `>`, `<=`, `>=`, `AND`, `OR`, `()`

## Use Cases

### Data Analysis

```bash
# Explore XML data
expocli "SELECT DISTINCT category FROM ./data"

# Find patterns
expocli "SELECT name, price FROM ./data WHERE category='books' ORDER BY price"
```

### Data Anonymization

```bash
# Encrypt sensitive data for testing
expocli-encrypt encrypt prod_data.xml test_data.xml -c config.yaml
```

### Interactive Exploration

Use Jupyter notebooks to:
- Explore data interactively
- Document analysis workflows
- Share reproducible queries
- Visualize results

## Project Structure

```
expocli/
├── src/                      # C++ source code
│   ├── main.cpp             # CLI entry point
│   ├── parser/              # Query parser
│   ├── executor/            # Query executor
│   └── utils/               # Utilities
├── expocli_crypto/          # Python encryption module
│   ├── cli.py              # Encryption CLI
│   ├── encryptor.py        # Main encryptor
│   ├── fpe.py              # Format-Preserving Encryption
│   └── pseudonymizer.py    # Data pseudonymization
├── expocli_kernel/          # Jupyter kernel
├── scripts/                 # Installation and utility scripts
├── tests/                   # Test suites
├── examples/                # Sample data
└── expocli_documentation/   # Full documentation
```

## Prerequisites

- **Docker** (recommended) or
- **C++17 compiler**, CMake 3.15+, pugixml, readline

## Contributing

Contributions welcome! See our documentation for:
- Code architecture
- Development setup
- Testing guidelines

## Troubleshooting

**Command not found after install:**
```bash
source ~/.bashrc  # Reload shell
```

**Permission denied:**
```bash
sudo usermod -aG docker $USER  # Add to docker group
# Log out and back in
```

**Docker proxy issues:**
See [Docker Proxy Fix](expocli_documentation/08b_Docker_Proxy_Fix.md)

**More help:**
See [Known Issues](expocli_documentation/09_Known_Issues.md)

## License

MIT License

## Links

- 📚 [Full Documentation](expocli_documentation/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
