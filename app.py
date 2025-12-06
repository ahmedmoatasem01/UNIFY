"""
Lightweight runner to allow `python app.py` from project root.
This executes `src/app.py` as __main__ so the existing Flask entrypoint runs.
"""
import runpy
import sys
import os

if __name__ == '__main__':
    # Ensure we run from repository root so relative paths in src/app.py still work
    repo_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_root)
    runpy.run_path(os.path.join('src', 'app.py'), run_name='__main__')
