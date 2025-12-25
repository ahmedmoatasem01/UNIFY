#!/usr/bin/env python3
"""
Local CI Check Runner
Runs the same checks that GitHub Actions will run
"""
import subprocess
import sys
import os


def run_command(name, command, fail_on_error=True):
    """Run a command and report results"""
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ {name} FAILED")
            if fail_on_error:
                return False
        else:
            print(f"✅ {name} PASSED")
        return True
    except Exception as e:
        print(f"❌ {name} ERROR: {e}")
        if fail_on_error:
            return False
        return True


def main():
    """Run all CI checks"""
    print("\n🚀 Starting Local CI Checks\n")
    
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"Working directory: {project_root}\n")
    
    results = []
    
    # 1. Syntax Check
    results.append(run_command(
        "Syntax Check (flake8)",
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        fail_on_error=True
    ))
    
    # 2. Code Style
    results.append(run_command(
        "Code Style (flake8)",
        "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
        fail_on_error=False
    ))
    
    # 3. Import Sorting
    results.append(run_command(
        "Import Sorting (isort)",
        "isort --check-only --diff src/ tests/",
        fail_on_error=False
    ))
    
    # 4. Code Formatting
    results.append(run_command(
        "Code Formatting (black)",
        "black --check --diff src/ tests/",
        fail_on_error=False
    ))
    
    # 5. Static Analysis
    results.append(run_command(
        "Static Analysis (pylint)",
        "pylint src/ --exit-zero",
        fail_on_error=False
    ))
    
    # 6. Security Scan
    results.append(run_command(
        "Security Scan (bandit)",
        "bandit -r src/ -f screen",
        fail_on_error=False
    ))
    
    # 7. Run Tests
    results.append(run_command(
        "Unit Tests",
        "python tests/run_tests.py",
        fail_on_error=True
    ))
    
    # 8. Test Coverage
    results.append(run_command(
        "Test Coverage (pytest)",
        "pytest tests/ --cov=src --cov-report=term --cov-report=html",
        fail_on_error=False
    ))
    
    # Summary
    print(f"\n{'='*80}")
    print("CI CHECK SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All critical checks passed!")
        print("Your code is ready to push! 🚀")
        return 0
    else:
        print("\n❌ Some checks failed!")
        print("Please fix the issues before pushing.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
