# Running UNIFY in Docker

## Prerequisites

1. Docker Desktop installed and running
2. SQL Server running on your host machine
3. Database `unify` created in SQL Server

## Important: SQL Server Configuration for Docker

When running the Flask app in Docker, it needs to connect to SQL Server on your host machine. SQL Server by default uses Windows Authentication, but Docker containers cannot use Windows Authentication. You have two options:

### Option 1: Use SQL Server Authentication (Recommended)

1. Enable SQL Server Authentication (Mixed Mode):
   - Open SQL Server Management Studio
   - Right-click on your server instance → Properties
   - Go to Security → Select "SQL Server and Windows Authentication mode"
   - Restart SQL Server service

2. Create a SQL login user:
   ```sql
   CREATE LOGIN docker_user WITH PASSWORD = 'YourSecurePassword123!';
   USE unify;
   CREATE USER docker_user FOR LOGIN docker_user;
   ALTER ROLE db_datareader ADD MEMBER docker_user;
   ALTER ROLE db_datawriter ADD MEMBER docker_user;
   ```

3. Update environment variables when running Docker:
   ```bash
   docker run -p 5000:5000 \
     -e DB_HOST=host.docker.internal \
     -e DB_NAME=unify \
     -e DB_USER=docker_user \
     -e DB_PASSWORD=YourSecurePassword123! \
     unify
   ```

### Option 2: Enable TCP/IP for SQL Server (Alternative)

1. Open SQL Server Configuration Manager
2. Go to SQL Server Network Configuration → Protocols for SQLEXPRESS
3. Enable TCP/IP
4. Right-click TCP/IP → Properties → IP Addresses tab
5. Scroll to IPAll section and set TCP Port to 1433 (or note the port)
6. Restart SQL Server service
7. Update connection string to use: `host.docker.internal,1433\SQLEXPRESS`

## Running with Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Running with Docker directly

```bash
# Build the image
docker build -t unify -f Docker/Dockerfile .

# Run the container
docker run -p 5000:5000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=unify \
  -e DB_USER=your_user \
  -e DB_PASSWORD=your_password \
  unify
```

## For Linux Docker (not Docker Desktop)

On Linux, `host.docker.internal` may not work. Use your host machine's IP address instead:

```bash
# Find your host IP (example)
ip addr show docker0 | grep inet

# Use that IP instead of host.docker.internal
docker run -p 5000:5000 \
  -e DB_HOST=172.17.0.1 \
  -e DB_NAME=unify \
  unify
```

## Troubleshooting

- **Connection refused**: Make sure SQL Server is running and TCP/IP is enabled
- **Authentication failed**: Check that SQL Server Authentication is enabled and credentials are correct
- **Can't connect to host.docker.internal**: On Linux, use the host's IP address instead

