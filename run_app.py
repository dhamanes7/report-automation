"""
Entry point for the packaged .exe. Boots Streamlit's own server against
app.py and opens the default browser — the client just double-clicks this.
No internet connection is made at any point.
"""
import os
import sys
import webbrowser
import threading

# Streamlit infers global.developmentMode from its own install path, treating
# anything without "site-packages" in __file__ as a dev checkout - which is
# always true once frozen by PyInstaller. That mode then rejects the
# --server.port flag below, so force it off before streamlit.config loads.
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

from streamlit.web import cli as stcli


def resource_path(rel_path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def open_browser():
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":
    threading.Timer(2.0, open_browser).start()
    sys.argv = [
        "streamlit", "run", resource_path("app.py"),
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())
