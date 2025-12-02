"""
Entry point script to run the Streamlit application.
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app", "main_ui.py")
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

