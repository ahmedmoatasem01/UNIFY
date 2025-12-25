# CI/CD Quick Reference

## 🚀 Quick Commands

### Run Locally (Before Pushing)

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linter
flake8 src/ tests/

# Run tests
pytest tests/ -v

# Run security scan
bandit -r src/ -ll
safety check

# Build Docker image
cd deployment
docker build -t unify-app:test .
```

---

## 📊 Pipeline Status

### GitHub Actions
- **View:** `https://github.com/your-username/unify/actions`
- **Status Badge:** Add to README.md:
  ```markdown
  ![CI/CD](https://github.com/your-username/unify/workflows/CI/CD%20Pipeline/badge.svg)
  ```

### GitLab CI
- **View:** `CI/CD > Pipelines` in GitLab
- **Status Badge:** Add to README.md:
  ```markdown
  ![pipeline status](https://gitlab.com/your-group/unify/badges/main/pipeline.svg)
  ```

---

## 🔍 Common Issues

| Issue | Solution |
|-------|----------|
| **Lint fails** | Run `black src/ tests/` and commit |
| **Tests fail** | Run `pytest tests/ -v` locally first |
| **Build fails** | Test with `docker build -t test .` |
| **Security warnings** | Review and update dependencies |

---

## 📝 Workflow Triggers

| Action | Trigger |
|--------|---------|
| Push to `main` | Full pipeline + deploy to production |
| Push to `develop` | Full pipeline + deploy to staging |
| Pull Request | Lint + Test + Security (no deploy) |
| Manual | Click "Run workflow" button |

---

## 🐳 Docker Images

### GitHub Container Registry
```bash
# Pull image
docker pull ghcr.io/your-username/unify-app:main

# Run locally
docker run -p 5000:5000 ghcr.io/your-username/unify-app:main
```

### GitLab Container Registry
```bash
# Pull image
docker pull registry.gitlab.com/your-group/unify/unify-app:main

# Run locally
docker run -p 5000:5000 registry.gitlab.com/your-group/unify/unify-app:main
```

---

## ✅ Pre-Push Checklist

Before pushing code:

- [ ] Code formatted: `black src/ tests/`
- [ ] Imports sorted: `isort src/ tests/`
- [ ] Tests passing: `pytest tests/ -v`
- [ ] No lint errors: `flake8 src/ tests/`
- [ ] Docker builds: `docker build -t test .`
- [ ] Health endpoint works: `curl http://localhost:5000/health`

---

## 🎯 Pipeline Stages

1. **Lint** → Code quality (5 min)
2. **Test** → Run tests (10-15 min)
3. **Security** → Scan for vulnerabilities (5 min)
4. **Build** → Create Docker image (15-20 min)
5. **Deploy** → Deploy to environment (5 min)

**Total:** ~40-50 minutes

---

## 📚 Full Documentation

See `deployment/CI_CD_SETUP.md` for complete setup guide.

