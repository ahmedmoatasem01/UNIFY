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
    src_path = os.path.join(repo_root, 'src')
    
    # Add src to Python path so imports work
    sys.path.insert(0, src_path)
    
    os.chdir(src_path)  # Change to src directory for app to find templates/static
    runpy.run_path(os.path.join(src_path, 'app.py'), run_name='__main__')
