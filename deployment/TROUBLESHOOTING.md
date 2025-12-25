# Docker Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Docker Desktop Not Running

**Error:**
```
error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Solution:**
1. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon in system tray should be steady)
   - Verify it's running: Look for Docker icon in Windows system tray

2. **Verify Docker is Running**
   ```powershell
   docker --version
   docker ps
   ```
   Both commands should work without errors.

3. **If Docker Desktop Won't Start:**
   - Restart Docker Desktop
   - Check Windows Services: Ensure "Docker Desktop Service" is running
   - Restart your computer if needed
   - Reinstall Docker Desktop if problem persists

---

### Issue 2: Obsolete `version` Warning

**Warning:**
```
the attribute `version` is obsolete, it will be ignored
```

**Solution:**
✅ **Fixed!** The `version` line has been removed from `docker-compose.yml`.

Modern Docker Compose (v2+) doesn't require the `version` field. The file has been updated.

---

### Issue 3: Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution:**
1. **Find what's using port 5000:**
   ```powershell
   netstat -ano | findstr :5000
   ```

2. **Stop the process or change port:**
   - Stop the conflicting application
   - Or change port in docker-compose.yml:
     ```yaml
     ports:
       - "5001:5000"  # Use 5001 instead
     ```

---

### Issue 4: Build Context Errors

**Error:**
```
failed to solve: failed to compute cache key
```

**Solution:**
1. **Ensure you're in the correct directory:**
   ```powershell
   cd deployment
   ```

2. **Check build context:**
   - The `context: ..` in docker-compose.yml means it looks for files in parent directory
   - Ensure `.dockerignore` exists in project root
   - Verify `deployment/Dockerfile` exists

---

### Issue 5: Permission Denied (Linux/WSL)

**Error:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

---

### Issue 6: Out of Disk Space

**Error:**
```
no space left on device
```

**Solution:**
1. **Clean up Docker:**
   ```powershell
   docker system prune -a
   docker volume prune
   ```

2. **Check disk space:**
   ```powershell
   docker system df
   ```

---

### Issue 7: Health Check Fails

**Error:**
```
Health check failed
```

**Solution:**
1. **Verify health endpoint exists:**
   - Check `src/app.py` has `/health` route
   - Test locally: `curl http://localhost:5000/health`

2. **Check container logs:**
   ```powershell
   docker-compose logs unify-app
   ```

3. **Increase start period:**
   ```yaml
   healthcheck:
     start_period: 60s  # Increase from 40s
   ```

---

## Quick Diagnostic Commands

### Check Docker Status
```powershell
# Docker version
docker --version

# Docker Compose version
docker-compose --version

# Docker info
docker info

# List running containers
docker ps

# List all containers
docker ps -a
```

### Check Build
```powershell
# Test Dockerfile build
cd deployment
docker build -t test-build -f Dockerfile ..

# Check image
docker images | findstr unify
```

### Check Compose
```powershell
# Validate docker-compose.yml
docker-compose config

# Dry run (no actual execution)
docker-compose up --dry-run
```

---

## Step-by-Step Setup

### 1. Verify Prerequisites
```powershell
# Check Docker Desktop is installed
docker --version

# Check Docker is running
docker ps
```

### 2. Navigate to Deployment Directory
```powershell
cd C:\Users\Dell\UNIFY\deployment
```

### 3. Build the Image
```powershell
docker-compose build
```

### 4. Start the Container
```powershell
docker-compose up -d
```

### 5. Check Status
```powershell
docker-compose ps
docker-compose logs -f unify-app
```

---

## Getting Help

### Check Logs
```powershell
# All services
docker-compose logs

# Specific service
docker-compose logs unify-app

# Follow logs
docker-compose logs -f unify-app

# Last 100 lines
docker-compose logs --tail=100 unify-app
```

### Inspect Container
```powershell
# Container details
docker inspect unify-app

# Execute command in container
docker-compose exec unify-app /bin/bash
docker-compose exec unify-app python --version
docker-compose exec unify-app whoami
```

### Clean Start
```powershell
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## Common Commands Reference

```powershell
# Build
docker-compose build
docker-compose build --no-cache

# Start
docker-compose up
docker-compose up -d  # Detached mode

# Stop
docker-compose stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Execute command
docker-compose exec unify-app <command>

# Check status
docker-compose ps

# Validate config
docker-compose config
```

---

## Still Having Issues?

1. **Check Docker Desktop:**
   - Is it running? (Check system tray)
   - Is it up to date?
   - Try restarting it

2. **Check System Requirements:**
   - Windows 10/11 64-bit
   - WSL 2 enabled (for Docker Desktop)
   - Virtualization enabled in BIOS

3. **Check Logs:**
   ```powershell
   docker-compose logs > docker-errors.log
   ```

4. **Try Clean Build:**
   ```powershell
   docker-compose down -v
   docker system prune -a
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## Prevention Tips

1. **Always start Docker Desktop** before running docker commands
2. **Keep Docker Desktop updated** to latest version
3. **Monitor disk space** - Docker images can be large
4. **Use .dockerignore** to reduce build context size
5. **Check logs regularly** to catch issues early

