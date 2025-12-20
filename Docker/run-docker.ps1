# PowerShell script to run UNIFY Docker container
# Run this script: .\run-docker.ps1

docker run -p 5000:5000 `
  -e DB_HOST=host.docker.internal `
  -e DB_NAME=unify `
  -e DB_USER=docker_user `
  -e "DB_PASSWORD=DockerUnify2024!@#" `
  unify

