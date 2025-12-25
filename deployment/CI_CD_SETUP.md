# CI/CD Pipeline Setup Guide

This guide explains how to set up and use the automated CI/CD pipeline for the UNIFY Flask application.

## 📋 Overview

The CI/CD pipeline automates:
- ✅ Code quality checks (linting, formatting)
- ✅ Security scanning (static analysis, dependency checks)
- ✅ Automated testing (unit, integration)
- ✅ Docker image building
- ✅ Container security scanning
- ✅ Automated deployment (staging & production)

---

## 🚀 Quick Start

### GitHub Actions (Recommended)

1. **Push code to GitHub** - The pipeline runs automatically on push/PR
2. **View workflows** - Go to `Actions` tab in your GitHub repository
3. **Monitor progress** - Watch real-time build logs

### GitLab CI

1. **Push code to GitLab** - Pipeline runs automatically
2. **View pipelines** - Go to `CI/CD > Pipelines` in GitLab
3. **Monitor jobs** - Click on pipeline to see job details

---

## 📁 Pipeline Files

### GitHub Actions
- **Location:** `.github/workflows/ci-cd.yml`
- **Triggers:** Push to main/develop, Pull Requests, Manual

### GitLab CI
- **Location:** `.gitlab-ci.yml`
- **Triggers:** Push to main/develop, Merge Requests

---

## 🔧 Setup Instructions

### GitHub Actions Setup

#### 1. Enable GitHub Actions
- Actions are enabled by default on GitHub repositories
- No additional setup needed if using public repos
- For private repos, ensure Actions are enabled in Settings

#### 2. Configure Secrets (Optional)
If you need to push to external registries or deploy:

1. Go to **Settings > Secrets and variables > Actions**
2. Add secrets:
   - `DOCKER_REGISTRY_USERNAME` - Docker registry username
   - `DOCKER_REGISTRY_PASSWORD` - Docker registry password
   - `DEPLOY_KEY` - SSH key for deployment (if needed)

#### 3. Container Registry Setup
The pipeline uses GitHub Container Registry (ghcr.io) by default:

- **No setup needed** - Uses `GITHUB_TOKEN` automatically
- **Image location:** `ghcr.io/your-username/unify-app`
- **Access:** Public for public repos, private for private repos

#### 4. Environment Setup
Configure deployment environments:

1. Go to **Settings > Environments**
2. Create environments:
   - **staging** - For develop branch
   - **production** - For main branch
3. Add environment variables if needed

### GitLab CI Setup

#### 1. Enable GitLab CI
- CI/CD is enabled by default
- Ensure `.gitlab-ci.yml` is in repository root

#### 2. Configure Variables
1. Go to **Settings > CI/CD > Variables**
2. Add variables:
   - `DOCKER_REGISTRY_USER` - Registry username
   - `DOCKER_REGISTRY_PASSWORD` - Registry password

#### 3. Container Registry
GitLab provides built-in container registry:

- **Location:** `registry.gitlab.com/your-group/your-project`
- **Access:** Automatic with GitLab CI/CD
- **No additional setup needed**

---

## 📊 Pipeline Stages

### 1. Lint Stage
**Purpose:** Code quality and formatting checks

**Tools:**
- **Black** - Code formatter
- **isort** - Import sorting
- **Flake8** - Linting

**What it checks:**
- Code formatting consistency
- Import organization
- Code style violations
- Complexity warnings

**Failure:** Non-blocking (warnings only)

---

### 2. Test Stage
**Purpose:** Run automated tests

**Tools:**
- **pytest** - Test runner
- **pytest-cov** - Coverage reporting

**What it does:**
- Runs all tests in `tests/` directory
- Generates coverage reports
- Uploads coverage to Codecov (GitHub Actions)

**Failure:** Blocks deployment

---

### 3. Security Scan Stage
**Purpose:** Find security vulnerabilities

**Tools:**
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability checker
- **Trivy** - Container security scanner

**What it checks:**
- Security vulnerabilities in code
- Vulnerable dependencies
- Container image vulnerabilities

**Failure:** Non-blocking (reports only)

---

### 4. Build Stage
**Purpose:** Build Docker image

**What it does:**
- Builds Docker image using `deployment/Dockerfile`
- Tags image with branch name and commit SHA
- Pushes to container registry
- Uses build cache for faster builds

**Failure:** Blocks deployment

---

### 5. Deploy Stage
**Purpose:** Deploy to environments

**Environments:**
- **Staging** - Auto-deploys from `develop` branch
- **Production** - Auto-deploys from `main` branch (GitHub) or manual (GitLab)

**What it does:**
- Pulls latest image
- Updates running containers
- Runs health checks
- Verifies deployment

---

## 🎯 Workflow Triggers

### Automatic Triggers

1. **Push to main/develop**
   - Runs full pipeline
   - Builds and deploys automatically

2. **Pull Request**
   - Runs lint, test, security, build
   - Does NOT deploy
   - Provides feedback before merge

3. **Manual Trigger**
   - GitHub: Use "Run workflow" button
   - GitLab: Use "Run pipeline" button

---

## 🔍 Viewing Results

### GitHub Actions

1. **Go to Actions tab**
2. **Click on workflow run**
3. **View individual jobs:**
   - Click job to see logs
   - Expand steps for details
   - Download artifacts

### GitLab CI

1. **Go to CI/CD > Pipelines**
2. **Click on pipeline**
3. **View jobs:**
   - Click job to see logs
   - Download artifacts
   - View coverage reports

---

## 📈 Coverage Reports

### GitHub Actions
- **Codecov integration** - Automatic upload
- **View:** Codecov dashboard or Actions artifacts

### GitLab CI
- **Built-in coverage** - Shows in pipeline
- **View:** CI/CD > Pipelines > Coverage badge

---

## 🐳 Docker Images

### Image Tags

Images are tagged with:
- **Branch name** - `main`, `develop`, `feature-branch`
- **Commit SHA** - `main-abc1234`
- **Latest** - `latest` (main branch only)

### Pulling Images

```bash
# GitHub Container Registry
docker pull ghcr.io/your-username/unify-app:main

# GitLab Container Registry
docker pull registry.gitlab.com/your-group/your-project/unify-app:main
```

---

## 🚨 Troubleshooting

### Pipeline Fails at Lint

**Problem:** Code formatting issues

**Solution:**
```bash
# Auto-fix formatting
black src/ tests/
isort src/ tests/

# Commit and push
git add .
git commit -m "Fix code formatting"
git push
```

---

### Pipeline Fails at Tests

**Problem:** Tests failing

**Solution:**
1. Run tests locally: `pytest tests/ -v`
2. Fix failing tests
3. Ensure test database is configured
4. Check test environment variables

---

### Docker Build Fails

**Problem:** Build errors

**Solution:**
1. Test build locally:
   ```bash
   cd deployment
   docker build -t test-image .
   ```
2. Check Dockerfile syntax
3. Verify requirements.txt
4. Check build logs for specific errors

---

### Security Scan Finds Issues

**Problem:** Vulnerabilities reported

**Solution:**
1. Review security reports
2. Update vulnerable dependencies:
   ```bash
   pip install --upgrade package-name
   ```
3. Update `requirements.txt`
4. Re-run pipeline

---

### Deployment Fails

**Problem:** Deployment step fails

**Solution:**
1. Check deployment scripts in workflow
2. Verify environment variables
3. Check server connectivity
4. Review deployment logs

---

## 🔐 Security Best Practices

### Secrets Management

1. **Never commit secrets** - Use CI/CD secrets/variables
2. **Rotate regularly** - Update secrets periodically
3. **Limit access** - Only grant necessary permissions
4. **Audit logs** - Review who accessed secrets

### Container Registry

1. **Use private registry** - For production images
2. **Scan images** - Enable Trivy scanning
3. **Tag properly** - Use semantic versioning
4. **Clean up old images** - Remove unused tags

---

## 📝 Customization

### Add Custom Steps

Edit `.github/workflows/ci-cd.yml` or `.gitlab-ci.yml`:

```yaml
# Example: Add database migration step
run-migrations:
  stage: deploy
  script:
    - docker run --rm $IMAGE python manage.py migrate
```

### Change Triggers

Modify `on:` section (GitHub) or `only:` section (GitLab):

```yaml
# GitHub Actions
on:
  push:
    branches: [ main, develop, release/* ]

# GitLab CI
only:
  - main
  - develop
  - /^release\/.*$/
```

### Add Notifications

```yaml
# Slack notification example
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎓 Advanced Features

### Matrix Testing
Test against multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

### Parallel Jobs
Run tests in parallel for faster execution:

```yaml
strategy:
  matrix:
    test-suite: [unit, integration, e2e]
```

### Caching
Speed up builds with caching:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

---

## ✅ Checklist

Before using the pipeline:

- [ ] Repository is on GitHub or GitLab
- [ ] `.github/workflows/ci-cd.yml` or `.gitlab-ci.yml` is committed
- [ ] Tests are passing locally
- [ ] Dockerfile builds successfully
- [ ] Health endpoint exists (`/health`)
- [ ] Secrets configured (if needed)
- [ ] Environments configured (for deployment)

---

## 🎉 Summary

Your CI/CD pipeline is now set up and ready to use! It will:

1. ✅ Check code quality on every push
2. ✅ Run tests automatically
3. ✅ Scan for security issues
4. ✅ Build Docker images
5. ✅ Deploy to staging/production

**Next Steps:**
1. Push code to trigger pipeline
2. Monitor first run
3. Customize as needed
4. Set up deployment targets

Happy deploying! 🚀

