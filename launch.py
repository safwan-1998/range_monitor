"""CLI entry point: python launch.py"""

import subprocess
import sys
import pathlib

app = pathlib.Path(__file__).parent / "app.py"
subprocess.run(
    [sys.executable, "-m", "streamlit", "run", str(app), "--server.port=8502"],
    check=True,
)
