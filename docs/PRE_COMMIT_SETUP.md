# Pre-commit Hook Setup (Optional)

This repository includes an optional pre-commit hook configuration to catch issues before they're committed.

## Quick Setup

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Install the git hooks:
```bash
pre-commit install
```

3. (Optional) Run against all files:
```bash
pre-commit run --all-files
```

## What It Does

The pre-commit hooks will automatically:
- ✅ Check Python syntax
- ✅ Format code with black
- ✅ Sort imports with isort
- ✅ Lint with flake8
- ✅ Check for common security issues
- ✅ Trim trailing whitespace
- ✅ Fix end-of-file formatting

## Bypassing Hooks

If you need to commit without running hooks (not recommended):
```bash
git commit --no-verify -m "Your message"
```

## Configuration

See `.pre-commit-config.yaml` for hook configuration details.

## Troubleshooting

**Issue**: Pre-commit fails with "command not found"
**Solution**: Ensure pre-commit is installed: `pip install pre-commit`

**Issue**: Hooks are slow
**Solution**: Pre-commit caches environments. First run is slow, subsequent runs are fast.

---

Note: Pre-commit hooks run locally on your machine. The CI pipeline on GitHub Actions will still run all checks regardless of local setup.
