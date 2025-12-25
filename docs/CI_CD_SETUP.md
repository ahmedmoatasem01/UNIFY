# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for Continuous Integration (CI) to automatically test, lint, and scan code on every push and pull request.

## Workflow Structure

The CI pipeline is defined in `.github/workflows/ci.yml` and consists of four main jobs:

### 1. **Test Job** 🧪
- **Purpose**: Runs all unit and integration tests
- **Matrix Strategy**: Tests against Python 3.9, 3.10, and 3.11
- **Steps**:
  - Checks out the code
  - Sets up Python environment
  - Caches pip dependencies for faster builds
  - Installs project dependencies
  - Runs linting checks with flake8
  - Executes test suite using `tests/run_tests.py`
  - Generates code coverage reports
  - Uploads coverage to Codecov (optional)
  - Archives test results as artifacts

### 2. **Lint Job** 🔍
- **Purpose**: Ensures code quality and style consistency
- **Tools Used**:
  - **black**: Code formatting checker
  - **isort**: Import statement sorting
  - **pylint**: Static code analysis
  - **flake8**: Style guide enforcement
- **Note**: Lint failures won't block the pipeline but will be reported

### 3. **Security Job** 🔒
- **Purpose**: Scans for security vulnerabilities
- **Tools Used**:
  - **Bandit**: Python security issue scanner
  - **Safety**: Dependency vulnerability checker
- **Output**: Generates security reports uploaded as artifacts

### 4. **Build Status Job** ✅
- **Purpose**: Final status check
- **Behavior**: Fails the entire pipeline if tests fail

## Triggers

The workflow automatically runs on:
- **Push** to `main`, `develop`, or `master` branches
- **Pull Requests** targeting `main`, `develop`, or `master` branches

## Setup Instructions

### 1. Push to GitHub
```bash
git add .github/
git commit -m "Add CI/CD pipeline with GitHub Actions"
git push origin main
```

### 2. Update README Badge
Replace `YOUR-USERNAME` in the README.md badge URL with your actual GitHub username:
```markdown
![CI Pipeline](https://github.com/YOUR-USERNAME/UNIFY/actions/workflows/ci.yml/badge.svg)
```

### 3. Enable GitHub Actions
1. Go to your GitHub repository
2. Click on the "Actions" tab
3. GitHub Actions should be enabled by default
4. You'll see the workflow run automatically on the next push

### 4. Optional: Setup Codecov (Code Coverage)
1. Visit [codecov.io](https://codecov.io/)
2. Sign in with your GitHub account
3. Add your repository
4. Copy the token
5. Add it as a secret in your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Your token
6. The workflow will automatically upload coverage reports

## Viewing Results

### GitHub Actions Dashboard
1. Navigate to your repository on GitHub
2. Click the "Actions" tab
3. View workflow runs, logs, and artifacts

### Artifacts
The pipeline archives the following artifacts (available for 30 days):
- Test reports (`test-results-<python-version>`)
- HTML coverage reports
- Security scan results (`security-reports`)

### Status Badges
The CI status badge in README.md will show:
- ✅ Green "passing" if all tests pass
- ❌ Red "failing" if any tests fail

## Local Testing

Before pushing, you can run the same checks locally:

### Run Tests
```bash
python tests/run_tests.py
```

### Run Linting
```bash
# Install tools
pip install flake8 pylint black isort

# Check formatting
black --check src/ tests/

# Check imports
isort --check-only src/ tests/

# Run pylint
pylint src/

# Run flake8
flake8 src/ tests/
```

### Run Security Scans
```bash
# Install tools
pip install bandit safety

# Security scan
bandit -r src/

# Dependency check
safety check
```

## Customization

### Modify Python Versions
Edit the matrix in `.github/workflows/ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Add More Tests
Simply add new test files to the `tests/` directory following the `test_*.py` naming convention.

### Adjust Branch Triggers
Modify the `on` section in the workflow file:
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main, develop ]
```

### Make Checks Required
In GitHub repository settings:
1. Go to Settings → Branches
2. Add branch protection rule for `main`
3. Check "Require status checks to pass before merging"
4. Select "test", "lint", and "security" checks

## Troubleshooting

### Tests Fail in CI but Pass Locally
- Ensure all dependencies are in `requirements.txt`
- Check for environment-specific issues
- Review the full error logs in GitHub Actions

### Workflow Doesn't Trigger
- Verify GitHub Actions is enabled
- Check that branch names match the trigger configuration
- Ensure `.github/workflows/ci.yml` is in the main branch

### Artifacts Not Uploading
- Check that the paths in the workflow match actual output locations
- Ensure the artifacts are created before the upload step

## Best Practices

1. **Write Tests First**: Follow TDD principles
2. **Keep Tests Fast**: Use mocking for external dependencies
3. **Monitor Coverage**: Aim for >80% code coverage
4. **Fix Failing Tests**: Don't ignore or disable failing tests
5. **Review Security Alerts**: Address Bandit and Safety warnings promptly
6. **Use Pre-commit Hooks**: Run linting locally before pushing

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [Codecov Documentation](https://docs.codecov.com/)
- [Bandit Security Scanner](https://bandit.readthedocs.io/)

## Support

For issues with the CI/CD pipeline:
1. Check GitHub Actions logs for detailed error messages
2. Review this documentation
3. Consult the GitHub Actions documentation
4. Open an issue in the repository

---

**Last Updated**: December 21, 2025
