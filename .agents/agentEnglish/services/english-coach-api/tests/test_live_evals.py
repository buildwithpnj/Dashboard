import pytest
import os
import json
import subprocess
import sys

def test_eval_runner_saves_run_reports():
    """Asserts that executing run_live_evals.py creates live_run_latest.json."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    latest_run_file = os.path.join(script_dir, "app", "tasks", "data", "evals", "runs", "live_run_latest.json")
    if os.path.exists(latest_run_file):
        os.remove(latest_run_file)
        
    # Execute python run_live_evals.py as a subprocess
    res = subprocess.run(
        [sys.executable, "scripts/run_live_evals.py"],
        cwd=script_dir,
        capture_output=True,
        text=True
    )
    
    # Assert run completes successfully (mock returns PASS)
    assert res.returncode == 0
    
    # Verify file was written
    # Check both paths where it can be written
    alt_run_file = os.path.join(script_dir, "data", "evals", "runs", "live_run_latest.json")
    assert os.path.exists(latest_run_file) or os.path.exists(alt_run_file)
