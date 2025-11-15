# expocli Installation Guide

This guide explains how to use expocli transparently on your local machine while it runs inside a Docker container.

## Quick Install (Recommended)

Run the automated installer:

```bash
cd /path/to/ExpoCLI
./install.sh
```

Then reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc for zsh users
```

That's it! You can now use `expocli` from anywhere.

## What the Installer Does

1. **Creates an alias** in your shell configuration (`~/.bashrc` or `~/.zshrc`)
2. **Links to the wrapper script** that handles all Docker operations transparently
3. **Tests the setup** to ensure everything works

## How It Works

The `expocli.sh` wrapper script automatically:

✅ **Starts** a persistent background container (if not running)
✅ **Builds** Docker image if needed (first time only)
✅ **Compiles** expocli binary if needed (first time only)
✅ **Maps** your current directory into the container
✅ **Executes** commands instantly (no container startup overhead)
✅ **Passes** all arguments transparently
✅ **Handles** interactive mode (REPL) and single queries
✅ **Preserves** exit codes for scripting

**The container runs in the background and executes queries instantly!**
**You won't even notice it's running in a container!**

## Usage Examples

### Interactive Mode (REPL)
```bash
expocli
# You'll see: expocli>
```

### Single Query Mode
```bash
expocli "SELECT breakfast_menu/food/name FROM ./examples WHERE breakfast_menu/food/calories < 500"
```

### Query Local Files
```bash
cd /path/to/your/xml/files
expocli "SELECT * FROM ."
```

The wrapper automatically mounts your current directory, so you can query files from anywhere on your system!

### Use in Scripts
```bash
#!/bin/bash
result=$(expocli "SELECT name FROM ./data WHERE price < 100")
echo "Found: $result"
```

## First Run

The first time you run `expocli`, it will:
1. Build the Docker image (~1 minute)
2. Compile the expocli binary (~30 seconds)
3. Start the persistent container in the background

**Subsequent runs are instant!** The container stays running in the background (using minimal resources) and responds immediately to your queries.

## Manual Setup (Alternative)

If you prefer not to use the installer, you can manually add this to your `~/.bashrc` or `~/.zshrc`:

```bash
alias expocli='/full/path/to/ExpoCLI/expocli.sh'
```

## Managing the Container

### Check Status
```bash
cd /path/to/ExpoCLI
docker compose ps
```

### Stop the Container
```bash
cd /path/to/ExpoCLI
docker compose down
# Container will auto-start on next expocli use
```

### Restart the Container
```bash
cd /path/to/ExpoCLI
docker compose restart
```

### View Container Logs
```bash
cd /path/to/ExpoCLI
docker compose logs -f
```

## Updating expocli

If you make code changes and want to rebuild:

```bash
# Stop the container first
cd /path/to/ExpoCLI
docker compose down

# Rebuild the binary
docker compose up -d
docker compose exec expocli bash -c "cd /app/build && rm -rf * && cmake .. && make"
```

The wrapper will automatically detect and use the new binary.

## Uninstalling

To remove expocli:

```bash
# Stop and remove the container
cd /path/to/ExpoCLI
docker compose down

# Remove the alias from your shell config
sed -i.bak '/alias expocli=/d' ~/.bashrc  # or ~/.zshrc

# Remove Docker image and volumes (optional)
cd /path/to/ExpoCLI
docker compose down --rmi all --volumes
```

## Troubleshooting

### "Docker is not installed"
Install Docker from: https://docs.docker.com/get-docker/

### "Docker Compose V2 is not available"
Update Docker to the latest version. Docker Compose V2 is built into modern Docker.

### expocli is slow or not responding
- Check if container is running: `cd /path/to/ExpoCLI && docker compose ps`
- If container is not running, it will auto-start on next use
- Check Docker is running: `docker ps`
- Check image exists: `docker images | grep expocli`
- Restart container: `cd /path/to/ExpoCLI && docker compose restart`

### "Permission denied" errors
Ensure the wrapper script is executable:
```bash
chmod +x /path/to/ExpoCLI/expocli.sh
```

### File path issues
The wrapper automatically maps your current directory into the container.
Your entire home directory is accessible, so you can query files from anywhere under `${HOME}`.

Example:
```bash
cd /home/user/myproject
expocli "SELECT name FROM ./xmlfiles"  # ✅ Works (relative path)
expocli "SELECT name FROM /home/user/myproject/xmlfiles"  # ✅ Works (absolute path)
cd /home/user/Documents
expocli "SELECT name FROM ../myproject/xmlfiles"  # ✅ Works (relative path)
```

**Note:** Only files under your home directory are accessible. Files outside (e.g., `/tmp`, `/opt`) are not mounted.

## Advanced Usage

### Disable Progress Messages
```bash
EXPOCLI_QUIET=1 expocli "SELECT ..."
```

### Run Without Alias
```bash
/path/to/ExpoCLI/expocli.sh "SELECT ..."
```

### Access Container Directly
```bash
cd /path/to/ExpoCLI
# For interactive shell in the running container
docker compose exec expocli bash

# Or start a new temporary container
docker compose run --rm expocli bash
```

## Benefits of This Approach

✅ **Fast** - Persistent container means instant command execution
✅ **Portable** - Works on Linux, macOS, and Windows (with WSL)
✅ **Consistent** - Same environment everywhere via Docker
✅ **Transparent** - Feels like a native command
✅ **Automatic** - Builds, compiles, and starts when needed
✅ **Clean** - No local dependencies to install
✅ **Lightweight** - Container uses minimal resources when idle
✅ **Flexible** - Can still access container directly if needed

---

For more information, see the main [README.md](README.md).
