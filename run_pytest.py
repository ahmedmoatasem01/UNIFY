"""
Pytest Test Runner
Runs all tests using pytest from the project root
"""
import sys
import os
import subprocess

# Get project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Change to project root
os.chdir(project_root)

# Run pytest
if __name__ == '__main__':
    # Run pytest with verbose output
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short'
    ], cwd=project_root)
    
    sys.exit(result.returncode)
