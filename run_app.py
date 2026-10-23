"""
Entry point script to run the Streamlit application.
Run from project root: python run_app.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app", "main_ui.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = script_dir
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", app_path],
        cwd=script_dir,
        env=env,
    )
    

