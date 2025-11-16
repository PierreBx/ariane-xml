# Docker Buildx Setup Guide

## About the Warning

When building with `--rebuild-docker`, you may see:

```
WARN[0000] Docker Compose is configured to build using Bake, but buildx isn't installed
```

**What this means:**
- Docker Compose wants to use Buildx (advanced build engine) but it's not installed
- Docker automatically falls back to the classic build method
- **Your builds still work** - this is just a performance optimization warning

## Should You Install Buildx?

### ✅ **Install Buildx if you want:**
- Faster builds (parallel layer building)
- Better caching between builds
- More efficient resource usage
- To eliminate the warning

### ⚠️ **You can skip Buildx if:**
- Your builds are fast enough
- You rarely rebuild Docker images
- You prefer simpler setup
- The warning doesn't bother you

## Option 1: Install Buildx (Recommended)

### Quick Install

Run the installation script:

```bash
./scripts/install_buildx.sh
```

This will:
1. Download the latest Buildx release from GitHub
2. Install it to `~/.docker/cli-plugins/`
3. Make it executable
4. Verify the installation

### Manual Install

If you prefer manual installation:

```bash
# Create plugins directory
mkdir -p ~/.docker/cli-plugins

# Download latest buildx (replace VERSION with latest from GitHub)
BUILDX_VERSION="0.12.0"  # Check https://github.com/docker/buildx/releases
curl -sSL "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-amd64" \
  -o ~/.docker/cli-plugins/docker-buildx

# Make executable
chmod +x ~/.docker/cli-plugins/docker-buildx

# Verify
docker buildx version
```

### Verify Installation

After installation:

```bash
docker buildx version
# Should output: github.com/docker/buildx vX.X.X ...
```

Now rebuild your project - the warning should be gone:

```bash
./install.sh --rebuild-docker
```

## Option 2: Ignore the Warning

If you don't want to install Buildx, you can safely ignore the warning. Your builds will work exactly the same using the classic Docker builder.

The warning appears only once at the start of the build and doesn't affect:
- Build success
- Image quality
- Container functionality
- Build correctness

## Buildx Benefits

Once installed, Buildx provides:

### **Faster Builds**
```
Classic builder:  Layer 1 → Layer 2 → Layer 3 → ...
Buildx:          Layer 1 ┐
                 Layer 2 ├─ Parallel ─→ Faster
                 Layer 3 ┘
```

### **Better Caching**
- Smarter layer reuse
- Content-based cache keys
- Cache import/export features

### **Advanced Features**
- Multi-platform builds (ARM + x86)
- Build secrets management
- BuildKit backend improvements

## Buildx vs Classic Builder

| Feature | Classic Builder | Buildx |
|---------|----------------|--------|
| Speed | Standard | Faster (parallel) |
| Caching | Basic | Advanced |
| Multi-platform | No | Yes |
| Output formats | Limited | Multiple |
| Build secrets | No | Yes |
| Resource usage | Higher | Optimized |

## Troubleshooting

### "Permission denied" when downloading

Run with your user (not sudo):
```bash
./scripts/install_buildx.sh
```

### "Command not found" after install

Restart your terminal or run:
```bash
hash -r
```

### Buildx not detected after install

Check installation:
```bash
ls -la ~/.docker/cli-plugins/docker-buildx
# Should show executable permissions
```

Make sure it's executable:
```bash
chmod +x ~/.docker/cli-plugins/docker-buildx
```

### Still seeing the warning

1. Verify buildx is installed:
   ```bash
   docker buildx version
   ```

2. If installed but warning persists, check Docker Compose version:
   ```bash
   docker compose version
   ```

3. Try updating Docker Compose if needed

## Additional Resources

- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Buildx GitHub Releases](https://github.com/docker/buildx/releases)
- [BuildKit Features](https://github.com/moby/buildkit)

## Quick Reference

```bash
# Install Buildx
./scripts/install_buildx.sh

# Verify installation
docker buildx version

# Use with rebuild
./install.sh --rebuild-docker
# Warning should be gone!

# Or ignore the warning - builds work either way
```

---

**Bottom line:** The warning is informational. Installing Buildx improves performance, but it's optional. Your builds work fine without it.
