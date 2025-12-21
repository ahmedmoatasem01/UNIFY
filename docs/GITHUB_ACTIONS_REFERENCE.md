# GitHub Actions CI/CD Quick Reference

## Quick Commands

### View Workflow Status
```bash
# Check latest workflow runs
gh run list --workflow=ci.yml

# View specific run details
gh run view <run-id>

# Watch a running workflow
gh run watch
```

### Trigger Manual Run
```bash
gh workflow run ci.yml
```

### Download Artifacts
```bash
# List artifacts for a run
gh run view <run-id> --log

# Download all artifacts
gh run download <run-id>
```

## Workflow File Location
`.github/workflows/ci.yml`

## What Triggers the Workflow?
- Push to `main`, `develop`, or `master` branches
- Pull requests to `main`, `develop`, or `master` branches

## Jobs Overview

| Job | Purpose | Can Fail Build |
|-----|---------|----------------|
| **test** | Run unit tests on Python 3.9, 3.10, 3.11 | ✅ Yes |
| **lint** | Code quality checks (black, isort, pylint) | ❌ No |
| **security** | Security vulnerability scans | ❌ No |
| **build-status** | Final status aggregation | ✅ Yes (if tests fail) |

## Common Issues & Solutions

### Issue: Workflow not running
**Solution**: 
- Ensure `.github/workflows/ci.yml` is in the repository root
- Check that Actions are enabled in repository settings
- Verify branch names match the trigger configuration

### Issue: Tests pass locally but fail in CI
**Solution**:
- Check that all dependencies are in `requirements.txt`
- Review environment variables needed
- Look at full logs in Actions tab

### Issue: Import errors in CI
**Solution**:
- Ensure `PYTHONPATH` is set correctly
- Check that all `__init__.py` files exist
- Verify relative imports are correct

### Issue: Module not found
**Solution**:
- Add missing package to `requirements.txt`
- Commit and push changes

## Branch Protection Rules (Recommended)

To enforce CI checks before merging:

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select: `test` status check
4. Save changes

## Environment Variables

If your tests need environment variables, add them as secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add your secrets (e.g., `DATABASE_URL`, `API_KEY`)
4. Update workflow to use them:
   ```yaml
   env:
     DATABASE_URL: ${{ secrets.DATABASE_URL }}
   ```

## Caching

The workflow caches pip dependencies to speed up builds:
- Cache key: Hash of `requirements.txt`
- Location: `~/.cache/pip`
- Benefit: Faster subsequent builds (from ~2min to ~30sec)

## Artifacts Retention

Test results and reports are stored as artifacts:
- **Retention period**: 30 days
- **Storage location**: Actions → Workflow run → Artifacts section
- **Includes**: Test reports, coverage HTML, security scans

## Badge URLs

Add these to your README.md (replace `USERNAME` and `REPO`):

```markdown
# CI Status
![CI](https://github.com/USERNAME/REPO/actions/workflows/ci.yml/badge.svg)

# Coverage (if using Codecov)
![Coverage](https://codecov.io/gh/USERNAME/REPO/branch/main/graph/badge.svg)

# Python Versions
![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)
```

## Running Tests Locally Before Push

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run the same checks as CI
python scripts/run_ci_checks.py
```

## Viewing Logs

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select a workflow run
4. Click on a job (e.g., "test")
5. View detailed logs with timestamps

## Notifications

GitHub will notify you of workflow results via:
- ✉️ Email (if enabled in settings)
- 🔔 GitHub notifications
- 💬 PR status checks

## Useful GitHub CLI Commands

```bash
# Install GitHub CLI (if not installed)
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Authenticate
gh auth login

# View workflow runs
gh run list

# View specific run
gh run view <run-id> --log

# Download artifacts
gh run download <run-id>

# Cancel a running workflow
gh run cancel <run-id>

# Rerun a failed workflow
gh run rerun <run-id>
```

## Cost & Usage Limits

GitHub Actions is free for public repositories:
- ✅ Unlimited minutes for public repos
- ✅ Unlimited concurrent jobs

For private repositories:
- Free: 2,000 minutes/month
- Check usage: Settings → Billing → Actions

---

**Pro Tip**: Use the badge in your README to show build status at a glance! 🎯
