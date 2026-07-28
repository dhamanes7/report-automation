"""
Entry point for the packaged .exe. Boots Streamlit's own server against
app.py and opens the default browser — the client just double-clicks this.
No internet connection is made at any point.

In a console=False build, sys.stdout/sys.stderr are None on Windows (no
console is attached), so any print/log call in streamlit, click, or tornado
would otherwise crash immediately with "'NoneType' object has no attribute
'write'" and the window would just vanish with zero information. Both are
redirected into an in-memory buffer before anything else runs, and that
buffer plus any traceback is flushed to error_log.txt next to the .exe on
failure — something the client can send back instead of "it just closes".
"""
import io
import os
import sys
import threading
import traceback
import webbrowser
from datetime import datetime


def app_dir():
    """Directory the .exe itself lives in. Not the onefile temp extraction
    dir (sys._MEIPASS), which PyInstaller deletes on exit — error_log.txt
    has to land somewhere the client can actually find and send back."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


LOG_PATH = os.path.join(app_dir(), "error_log.txt")

_captured_output = io.StringIO()
if sys.stdout is None:
    sys.stdout = _captured_output
if sys.stderr is None:
    sys.stderr = _captured_output

# Streamlit infers global.developmentMode from its own install path, treating
# anything without "site-packages" in __file__ as a dev checkout - which is
# always true once frozen by PyInstaller. That mode then rejects the
# --server.port flag below, so force it off before streamlit.config loads.
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"


def resource_path(rel_path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def open_browser():
    webbrowser.open("http://localhost:8501")


def write_crash_log(exc=None):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n--- {datetime.now().isoformat(timespec='seconds')} ---\n")
        if exc is not None:
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=f)
        captured = _captured_output.getvalue().strip()
        if captured:
            f.write("--- captured output ---\n")
            f.write(captured + "\n")


def main():
    from streamlit.web import cli as stcli

    threading.Timer(2.0, open_browser).start()
    sys.argv = [
        "streamlit", "run", resource_path("app.py"),
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    return stcli.main()


if __name__ == "__main__":
    try:
        exit_code = main()
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
        if exit_code:
            write_crash_log(exc)
        sys.exit(exit_code)
    except BaseException as exc:
        write_crash_log(exc)
        sys.exit(1)
    else:
        if exit_code:
            write_crash_log()
        sys.exit(exit_code)
