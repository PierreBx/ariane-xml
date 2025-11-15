# ExpoCLI Quick Start - Jupyter Notebook

Get started with ExpoCLI in Jupyter notebooks for interactive data exploration and analysis.

## Why Jupyter?

- 📊 **Cell-based execution** with persistent results
- 📝 **Mix queries with documentation** and visualizations
- 🔄 **Reproducible workflows** saved as `.ipynb` files
- 🎓 **Perfect for tutorials** and data exploration

## Installation

### Option 1: Docker (Recommended)

```bash
# Start Jupyter Lab with everything pre-configured
docker compose up -d jupyter

# Open browser to http://localhost:8888
# Navigate to examples/ExpoCLI_Demo.ipynb
```

### Option 2: Host Installation

```bash
# Install the Jupyter kernel on your host
./install_kernel.sh

# Start Jupyter
jupyter notebook

# Open the demo: examples/ExpoCLI_Demo.ipynb
```

## Basic Usage

### Creating Your First Notebook

1. Open Jupyter Lab (http://localhost:8888)
2. Create a new notebook
3. Select **"ExpoCLI"** as the kernel
4. Start querying!

### Running Queries

Simply type your SQL-like query in a cell:

```sql
SELECT breakfast_menu/food/name FROM /app/examples WHERE breakfast_menu/food/calories < 700
```

Press `Shift+Enter` to run.

Output:
```
Belgian Waffles
French Toast

2 row(s) returned.
```

### Multiple Queries in One Notebook

```sql
-- Cell 1: Get all items
SELECT name, price FROM /app/examples

-- Cell 2: Filter by price
SELECT name FROM /app/examples WHERE price < 6

-- Cell 3: Complex analysis
SELECT FILE_NAME, name, price, calories
FROM /app/examples
WHERE (price < 10 AND calories > 500)
ORDER BY price
```

## Features

### Persistent Results

Results stay in the notebook - perfect for sharing analyses!

### Mix with Markdown

```markdown
# My Analysis

Let's find low-calorie options:
```

```sql
SELECT name FROM /app/examples WHERE calories < 600
```

```markdown
## Results

The query found 2 items...
```

### Export Options

- **PDF**: File → Export Notebook As → PDF
- **HTML**: File → Export Notebook As → HTML
- **Python**: File → Export Notebook As → Executable Script

## Example Workflow

### 1. Data Exploration

```sql
-- See what's in the data
SELECT DISTINCT FILE_NAME FROM /app/examples
```

### 2. Initial Query

```sql
-- Find items under $7
SELECT name, price FROM /app/examples WHERE price < 7
```

### 3. Refinement

```sql
-- Add more criteria
SELECT name, price, calories
FROM /app/examples
WHERE price < 7 AND calories < 800
```

### 4. Visualization (Coming Soon)

```python
# Convert results to pandas for plotting
import pandas as pd
# Plot results...
```

## Demo Notebook

Check out `examples/ExpoCLI_Demo.ipynb` for:
- Basic queries
- Advanced filtering
- Multi-file queries
- Real-world examples

## Tips

1. **Use `/app/` prefix** for paths in Docker
2. **Document your queries** with markdown cells
3. **Save frequently** - work is persistent
4. **Share notebooks** - they're self-contained

## Keyboard Shortcuts

- `Shift+Enter` - Run cell and move to next
- `Ctrl+Enter` - Run cell and stay
- `Alt+Enter` - Run cell and insert below
- `Esc` then `A` - Insert cell above
- `Esc` then `B` - Insert cell below
- `Esc` then `DD` - Delete cell

## Advanced Features

### Mixing with Python

```python
# Cell 1 (Python)
import os
data_dir = "/app/examples"
print(f"Searching in: {data_dir}")
```

```sql
-- Cell 2 (ExpoCLI)
SELECT name FROM /app/examples
```

### Error Handling

If a query fails, you'll see:
```
Error: Invalid query syntax
Check your WHERE clause...
```

Fix the query and re-run the cell!

## Troubleshooting

### Kernel Not Found

```bash
# Re-install the kernel
python3 -m expocli_kernel.install

# Restart Jupyter
docker compose restart jupyter
```

### Connection Issues

```bash
# Check Jupyter is running
docker compose ps

# View logs
docker compose logs jupyter

# Restart if needed
docker compose restart jupyter
```

### Kernel Keeps Restarting

Check the logs:
```bash
docker compose logs jupyter | tail -50
```

## Next Steps

- 📖 Full [Jupyter Integration Guide](04_Jupyter_Integration.md)
- 🚀 Try the [CLI interface](01a_Quick_Start_CLI.md)
- 🔐 Learn about [encryption](01c_Quick_Start_Encryption.md)
- 📚 Explore [advanced examples](04b_Jupyter_Technical_Analysis.md)

## Resources

- **Demo Notebook**: `examples/ExpoCLI_Demo.ipynb`
- **Jupyter Docs**: https://jupyter.org/documentation
- **ExpoCLI Full Docs**: See [main README](../README.md)
