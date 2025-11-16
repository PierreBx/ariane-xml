# Ariane-XML Quick Start - Command Line Interface

Get started with Ariane-XML in 5 minutes using the command-line interface.

## Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ariane-xml

# Run the installer (installs transparent local command)
./install.sh

# Reload your shell
source ~/.bashrc  # or ~/.zshrc for zsh
```

The first run builds the Docker image automatically (~1-2 minutes). Subsequent runs are instant!

### Local Build

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install build-essential cmake libpugixml-dev libreadline-dev

# Build
mkdir build && cd build
cmake ..
make

# Run
./ariane-xml
```

## Basic Usage

### Interactive Mode (REPL)

Start the interactive shell:

```bash
ariane-xml
```

Run queries interactively:

```
ariane-xml> SELECT breakfast_menu/food/name FROM ./examples WHERE breakfast_menu/food/calories < 700
Belgian Waffles
French Toast

2 row(s) returned.

ariane-xml> exit
```

### Single Query Mode

Execute one-off queries from the command line:

```bash
ariane-xml "SELECT name FROM ./data WHERE price < 30"
```

## Query Syntax

### Basic Structure

```sql
SELECT <field>[,<field>...] FROM <path> [WHERE <condition>] [ORDER BY <field>] [LIMIT n]
```

### Field Paths

Use dot or slash notation:
- `breakfast_menu.food.name`
- `breakfast_menu/food/name`

### Examples

**Simple query:**
```sql
SELECT breakfast_menu/food/name FROM ./examples
```

**With conditions:**
```sql
SELECT name FROM ./examples WHERE price < 10
```

**Multiple fields with filename:**
```sql
SELECT FILE_NAME,name,price FROM ./examples WHERE calories > 500
```

**Ordered results:**
```sql
SELECT name FROM ./examples ORDER BY price LIMIT 5
```

**Complex conditions:**
```sql
SELECT name FROM ./data WHERE (price < 50 AND calories < 1000) OR rating > 4
```

## Sample Data

Try with the included examples:

```bash
# List all breakfast items
ariane-xml "SELECT breakfast_menu/food/name FROM ./examples"

# Find items under $6
ariane-xml "SELECT name,price FROM ./examples WHERE price < 6"

# Query across multiple files
ariane-xml "SELECT FILE_NAME,name FROM ./examples WHERE calories < 700"
```

## Interactive Commands

In REPL mode:
- `help`, `\h`, `\?` - Show help
- `exit`, `quit`, `\q` - Exit
- `\c`, `clear` - Clear screen
- `\` at end of line - Continue query on next line

## Tips

1. **Use FILE_NAME** to see which file contains each result
2. **Quote your queries** in single-query mode if they contain spaces
3. **Arrow keys** work in interactive mode for command history
4. **Tab completion** is available for paths (coming soon)

## Next Steps

- 📖 Read the [full documentation](../README.md)
- 🚀 Try [Jupyter integration](01b_Quick_Start_Jupyter.md)
- 🔐 Learn about [encryption](01c_Quick_Start_Encryption.md)
- 📚 See [advanced examples](02_Installation_Guide.md#advanced-usage)

## Troubleshooting

**Command not found:**
```bash
# Reload shell after install
source ~/.bashrc

# Or use Docker directly
docker compose exec ariane-xml /app/build/ariane-xml
```

**Permission denied:**
```bash
# Add to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**See also:** [Known Issues](09_Known_Issues.md)
