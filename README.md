# Ariane-XML

A high-performance SQL-like query tool for XML files with encryption capabilities.

## Features

- 🔍 **SQL-like Query Syntax** - Familiar SELECT/FROM/WHERE/ORDER BY/LIMIT syntax
- 🚀 **Interactive & Batch Modes** - REPL interface or single-query execution
- 📊 **Jupyter Integration** - Run queries in notebooks for data exploration
- 🔐 **XML Encryption** - Format-preserving encryption and French data pseudonymization
- ⚡ **High Performance** - Built with C++17 and pugixml
- 🐳 **Docker Support** - Consistent environment, works anywhere

## Quick Start

### Using the Management Console (Recommended)

The easiest way to get started is using the unified management script:

```bash
# Clone the repository
git clone <repository-url>
cd ariane-xml

# Launch the interactive manager
./ariane-xml-manager.sh
```

The manager provides an interactive menu for:
- 🛠️ **Setup** - Installation and environment checks
- 📚 **Documentation** - Quick access to all guides
- 🐳 **Environment** - Container management
- 🚀 **Apps** - Start CLI or Jupyter
- 🧪 **Tests** - Run test suites

**Non-interactive mode:**
```bash
./ariane-xml-manager.sh --help        # Show all options
./ariane-xml-manager.sh --install     # Run installation
./ariane-xml-manager.sh --check-env   # Check environment
./ariane-xml-manager.sh --cli         # Start CLI
./ariane-xml-manager.sh --jupyter     # Start Jupyter
./ariane-xml-manager.sh --test-light  # Run tests
```

### Manual Installation

```bash
# Clone and install (creates transparent local command)
git clone <repository-url>
cd ariane-xml
./ariane-xml-scripts/install.sh

# Reload shell
source ~/.bashrc
```

### Run a Query

```bash
# Interactive mode
ariane-xml

# Single query
ariane-xml "SELECT name FROM ./data WHERE price < 30"
```

### Example Queries

```sql
-- Simple query
SELECT breakfast_menu/food/name FROM ./ariane-xml-examples

-- With conditions
SELECT name, price FROM ./ariane-xml-examples WHERE price < 10

-- Multiple files with ordering
SELECT FILE_NAME, name FROM ./data WHERE calories < 500 ORDER BY price LIMIT 10

-- Complex conditions
SELECT name FROM ./data WHERE (price < 50 AND calories < 1000) OR rating > 4
```

## Documentation

### Quick Start Guides (5 minutes each)

- 📘 [CLI Quick Start](ariane-xml-documentation/01a_Quick_Start_CLI.md) - Command-line interface
- 📙 [Jupyter Quick Start](ariane-xml-documentation/01b_Quick_Start_Jupyter.md) - Notebook interface
- 📗 [Encryption Quick Start](ariane-xml-documentation/01c_Quick_Start_Encryption.md) - XML encryption

### Detailed Documentation

- [Installation Guide](ariane-xml-documentation/02_Installation_Guide.md) - Complete installation instructions
- [Jupyter Integration](ariane-xml-documentation/04_Jupyter_Integration.md) - Full Jupyter documentation
- [Encryption Module](ariane-xml-documentation/07_Encryption_Module.md) - Complete encryption reference
- [Known Issues](ariane-xml-documentation/09_Known_Issues.md) - Troubleshooting guide
- [Architecture](ariane-xml-documentation/10_Architecture_Diagram.md) - System architecture

## Main Components

### 1. Ariane-XML (Query Engine)

Query XML files using SQL-like syntax:

```bash
ariane-xml "SELECT name, price FROM ./data WHERE price < 50"
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
SELECT name FROM /app/ariane-xml-examples WHERE calories < 600
```

**Features:**
- Cell-based execution
- Persistent results
- Mix queries with documentation
- Export to PDF/HTML

### 3. XML Encryption (ariane-xml-encrypt)

Encrypt and pseudonymize XML data:

```bash
ariane-xml-encrypt encrypt input.xml encrypted.xml -c config.yaml
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
ariane-xml "SELECT DISTINCT category FROM ./data"

# Find patterns
ariane-xml "SELECT name, price FROM ./data WHERE category='books' ORDER BY price"
```

### Data Anonymization

```bash
# Encrypt sensitive data for testing
ariane-xml-encrypt encrypt prod_data.xml test_data.xml -c config.yaml
```

### Interactive Exploration

Use Jupyter notebooks to:
- Explore data interactively
- Document analysis workflows
- Share reproducible queries
- Visualize results

## Project Structure

```
ariane-xml/
├── ariane-xml-c-kernel/        # C++ query engine
│   ├── src/                    # C++ source code
│   │   ├── main.cpp           # CLI entry point
│   │   ├── parser/            # Query parser
│   │   ├── executor/          # Query executor
│   │   └── utils/             # Utilities
│   ├── include/               # Header files
│   └── build/                 # Build output directory
├── ariane-xml-crypto/         # Python encryption module
│   ├── cli.py                 # Encryption CLI
│   ├── encryptor.py           # Main encryptor
│   ├── fpe.py                 # Format-Preserving Encryption
│   └── pseudonymizer.py       # Data pseudonymization
├── ariane-xml-jupyter-kernel/ # Jupyter kernel
├── ariane-xml-scripts/        # Installation and utility scripts
├── ariane-xml-tests/          # Test suites
├── ariane-xml-examples/       # Sample data
└── ariane-xml-documentation/  # Full documentation
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
See [Docker Proxy Fix](ariane-xml-documentation/08b_Docker_Proxy_Fix.md)

**More help:**
See [Known Issues](ariane-xml-documentation/09_Known_Issues.md)

## License

MIT License

## Links

- 📚 [Full Documentation](ariane-xml-documentation/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
