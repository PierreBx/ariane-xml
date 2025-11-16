# How to Fix Docker Proxy and Rebuild with Encryption Module

## The Issue

Your Docker daemon is configured to use a proxy at `localhost:3128` that isn't running. This prevents building Docker images and downloading packages inside containers.

## The Solution - Step by Step

### Step 1: Fix Docker Proxy Configuration

Run the automated fix script:

```bash
cd /home/ipro0800/Documents/projets-perso/prod-projects/ariane-xml
./fix_docker_proxy.sh
```

This script will:
- Backup your current Docker daemon configuration
- Remove the proxy configuration
- Restart Docker daemon
- Verify the fix

**Note:** The script will ask for your sudo password.

### Step 2: Verify Docker is Working

Check that Docker daemon is running without proxy errors:

```bash
docker info | grep -i proxy
```

You should see empty or no proxy configuration.

### Step 3: Rebuild the Ariane-XML Image

Now that Docker can access the internet, rebuild the image with all encryption dependencies:

```bash
# Stop any running containers
docker compose down

# Rebuild the image (this will take a few minutes)
docker compose build

# Start the services
docker compose up -d
```

### Step 4: Verify the Encryption Module

Test that the encryption module is installed:

```bash
# Check if ariane-xml-encrypt is available
docker compose exec ariane-xml ariane-xml-encrypt --help

# Check if Python packages are installed
docker compose exec ariane-xml python3 -c "import cryptography, faker, lxml; print('All packages installed!')"
```

### Step 5: Test Encryption with Sample Data

```bash
# Enter the container
docker compose exec ariane-xml bash

# Navigate to test directory
cd /app/tests/encryption

# Encrypt the sample data
ariane-xml-encrypt encrypt sample_data.xml encrypted_sample.xml -c ../../ariane-xml-config/encryption_config.example.yaml
# Password: test123

# View the encrypted file
head -20 encrypted_sample.xml

# Decrypt it back
ariane-xml-encrypt decrypt encrypted_sample.xml decrypted_sample.xml -c ../../ariane-xml-config/encryption_config.example.yaml
# Password: test123

# Compare - should be identical
diff sample_data.xml decrypted_sample.xml

# Exit container
exit
```

### Step 6: Verify Jupyter is Working

```bash
# Check Jupyter logs
docker compose logs jupyter

# You should see something like:
#     To access the server, open this file in a browser:
#         file:///root/.local/share/jupyter/runtime/jpserver-X-open.html
#     Or copy and paste one of these URLs:
#         http://localhost:8888/lab?token=...

# Open browser to http://localhost:8888
```

## Alternative: Manual Fix (If Script Fails)

If the automated script doesn't work, here's the manual process:

### 1. Edit Docker daemon configuration

```bash
sudo nano /etc/docker/daemon.json
```

### 2. Replace the content with:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Important:** Remove any `"proxies"` configuration.

### 3. Save and exit (Ctrl+X, Y, Enter)

### 4. Restart Docker

```bash
sudo systemctl restart docker
```

### 5. Verify

```bash
docker info | grep -i proxy
sudo systemctl status docker
```

## Troubleshooting

### Issue: "permission denied while trying to connect to Docker daemon"

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### Issue: Docker build still fails with proxy error

Check if there are environment variables set:

```bash
env | grep -i proxy
```

If you see proxy variables, unset them:

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

Then try building again.

### Issue: "apt-get update" fails in container

This means the proxy configuration is still active. Double-check:

```bash
# Check Docker daemon config
sudo cat /etc/docker/daemon.json

# Check Docker info
docker info | grep -i proxy

# Restart Docker daemon
sudo systemctl restart docker
```

### Issue: Jupyter still shows old error

The container needs to be recreated with the new image:

```bash
docker compose down
docker compose build
docker compose up -d jupyter
docker compose logs -f jupyter
```

## Success Indicators

You'll know everything is working when:

1. ✅ `docker info | grep -i proxy` shows no proxy or empty values
2. ✅ `docker compose build` completes without connection errors
3. ✅ `docker compose exec ariane-xml ariane-xml-encrypt --help` shows the help message
4. ✅ `docker compose logs jupyter` shows Jupyter server started successfully
5. ✅ You can access Jupyter at http://localhost:8888

## Next Steps After Success

1. **Read the encryption documentation:**
   - `ENCRYPTION_QUICKSTART.md` - Quick start guide
   - `ENCRYPTION_MODULE.md` - Full documentation

2. **Customize your configuration:**
   ```bash
   cp ariane-xml-config/encryption_config.example.yaml my_config.yaml
   nano my_config.yaml
   ```

3. **Run the tests:**
   ```bash
   docker compose exec ariane-xml python3 -m pytest tests/encryption/test_encryption.py -v
   ```

4. **Try encrypting your own XML files:**
   ```bash
   docker compose exec ariane-xml bash
   ariane-xml-encrypt encrypt input.xml output.xml -c my_config.yaml
   ```

## Need More Help?

- Check `DOCKER_PROXY_FIX.md` for additional proxy troubleshooting
- Check `ENCRYPTION_IMPLEMENTATION_SUMMARY.md` for technical details
- Look at the test files in `tests/encryption/` for examples
