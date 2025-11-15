# Docker Proxy Configuration Fix

## Problem

Docker is configured to use a proxy at `localhost:3128` but the proxy server is not running, causing builds to fail with:

```
failed to do request: proxyconnect tcp: dial tcp 127.0.0.1:3128: connect: connection refused
```

## Solution Options

### Option 1: Disable Docker Proxy (Recommended if you don't need a proxy)

1. **Edit Docker daemon configuration:**
   ```bash
   sudo nano /etc/docker/daemon.json
   ```

2. **Remove or comment out proxy settings**, or set it to:
   ```json
   {
     "proxies": {}
   }
   ```

3. **If the file has proxy settings like this, remove them:**
   ```json
   {
     "proxies": {
       "default": {
         "httpProxy": "http://localhost:3128",
         "httpsProxy": "http://localhost:3128"
       }
     }
   }
   ```

4. **Restart Docker daemon:**
   ```bash
   sudo systemctl restart docker
   ```

5. **Verify the change:**
   ```bash
   docker info | grep -i proxy
   ```
   Should show empty or no proxy.

6. **Rebuild the image:**
   ```bash
   cd /home/ipro0800/Documents/projets-perso/prod-projects/expocli
   docker compose build
   ```

### Option 2: Use Direct Docker Build (Bypass Compose)

If you can't modify the daemon config, build directly with Docker:

```bash
# Build the image without using compose
docker build -t expocli_image:latest .

# Then start compose services
docker compose up -d
```

### Option 3: Manual Installation in Existing Container

Use the existing container and install dependencies manually:

```bash
# Start the existing container
docker compose up -d expocli

# Enter the container
docker compose exec expocli bash

# Update apt and install dependencies
apt-get update
apt-get install -y python3 python3-pip

# Install Python packages
pip3 install --no-cache-dir \
    jupyterlab \
    notebook \
    ipykernel \
    jupyter-client \
    cryptography \
    pyyaml \
    faker \
    lxml \
    ff3

# Install ExpoCLI packages
pip3 install -e .
python3 -m expocli_kernel.install
pip3 install -e . -f setup_crypto.py

# Verify installation
jupyter --version
expocli-encrypt --help
```

### Option 4: Start the Proxy Server (If you need a proxy)

If you actually need a proxy, you can install and configure one:

```bash
# Install squid proxy
sudo apt-get install squid

# Start squid
sudo systemctl start squid
sudo systemctl enable squid
```

## Quick Fix (Option 3 - Fastest)

Since you have an existing container, here's the quickest way:

```bash
docker compose up -d expocli
docker compose exec expocli bash -c "
    apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install jupyterlab notebook ipykernel jupyter-client cryptography pyyaml faker lxml ff3 && \
    pip3 install -e . && \
    python3 -m expocli_kernel.install && \
    pip3 install -e . -f setup_crypto.py
"
```

Then restart Jupyter:
```bash
docker compose restart jupyter
docker compose logs jupyter
```

## Recommended Long-term Fix

**Option 1** (disable proxy) is the best long-term solution if you don't need a proxy for Docker. This ensures future builds work correctly.
