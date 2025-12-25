# Production Deployment Guide

This directory contains Docker configuration files for deploying the UNIFY Flask application in production.

## Files

- `Dockerfile` - Production Docker image definition
- `docker-compose.yml` - Production Docker Compose configuration
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template (create `.env` file from this)

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root (parent directory) with your production settings:

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Database configuration
DB_TYPE=sqlite
SQLITE_DB_NAME=unify_prod.db

# Or for SQL Server/MySQL/PostgreSQL:
# DB_TYPE=sqlserver
# DB_HOST=your-db-host
# DB_NAME=unify
# DB_USER=your-user
# DB_PASSWORD=your-password
```

**Important:** Never commit the `.env` file to version control!

### 2. Build and Start

```bash
# From the deployment directory
docker-compose up -d

# Or from project root
cd deployment
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check container status
docker-compose ps

# Check health
curl http://localhost:5000/health

# Check logs
docker-compose logs -f unify-app
```

## Production Features

### Security
- ✅ Production mode (DEBUG=0)
- ✅ Secure session cookies
- ✅ Environment-based secret management
- ✅ No source code volume mounts
- ✅ Resource limits configured

### Reliability
- ✅ Health checks configured
- ✅ Automatic restart on failure
- ✅ Log rotation (10MB max, 3 files)
- ✅ Persistent data volumes

### Observability
- ✅ Structured logging
- ✅ Health check endpoint (`/health`)
- ✅ Readiness check endpoint (`/ready`)
- ✅ Container resource monitoring

## Environment Variables

### Required
- `SECRET_KEY` - Flask secret key (generate with `openssl rand -hex 32`)

### Database Configuration
- `DB_TYPE` - Database type: `sqlite`, `sqlserver`, `mysql`, or `postgresql`
- `DB_HOST` - Database host (required for non-SQLite)
- `DB_NAME` - Database name
- `DB_USER` - Database user (required for non-SQLite)
- `DB_PASSWORD` - Database password (required for non-SQLite)

### Optional
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `MULTI_TENANT_MODE` - Enable multi-tenant mode (default: `false`)
- `LLM_PROVIDER` - LLM provider (default: `ollama`)
- `OLLAMA_URL` - Ollama service URL (default: `http://ollama:11434`)

## Volumes

The following volumes are created for data persistence:

- `unify-data` - Database files (SQLite) and application data
- `unify-uploads` - User uploaded files
- `unify-logs` - Application logs

## Health Checks

The container includes health checks that verify:
- Application is responding on port 5000
- Health endpoint returns 200 OK

Health check runs every 30 seconds with a 10-second timeout.

## Resource Limits

Default resource limits:
- **CPU Limit:** 2.0 cores
- **Memory Limit:** 2GB
- **CPU Reservation:** 0.5 cores
- **Memory Reservation:** 512MB

Adjust in `docker-compose.yml` under `deploy.resources` if needed.

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs unify-app

# Check if port is already in use
netstat -an | grep 5000
```

### Database connection issues
- Verify database credentials in `.env`
- Check database is accessible from container
- For SQL Server, ensure ODBC driver is installed in image

### Health check failing
```bash
# Check if application is running
docker-compose exec unify-app curl http://localhost:5000/health

# Check application logs
docker-compose logs unify-app | tail -50
```

### View logs
```bash
# Follow logs
docker-compose logs -f unify-app

# Last 100 lines
docker-compose logs --tail=100 unify-app
```

## Updating the Application

```bash
# Rebuild and restart
docker-compose up -d --build

# Or rebuild specific service
docker-compose build unify-app
docker-compose up -d unify-app
```

## Stopping the Application

```bash
# Stop containers (keeps volumes)
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Backup

To backup persistent data:

```bash
# Backup volumes
docker run --rm -v unify-data:/data -v $(pwd):/backup alpine tar czf /backup/unify-data-backup.tar.gz /data
docker run --rm -v unify-uploads:/data -v $(pwd):/backup alpine tar czf /backup/unify-uploads-backup.tar.gz /data
```

## Production Checklist

Before deploying to production:

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Configure production database
- [ ] Set `FLASK_ENV=production` and `FLASK_DEBUG=0`
- [ ] Review and adjust resource limits
- [ ] Set up log aggregation/monitoring
- [ ] Configure reverse proxy (Nginx/Traefik) for HTTPS
- [ ] Set up database backups
- [ ] Test health check endpoints
- [ ] Review security settings
- [ ] Set up error tracking (Sentry, etc.)

## Reverse Proxy Setup (Nginx Example)

For production, use a reverse proxy for HTTPS:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Support

For issues or questions, refer to the main project README or open an issue.

