"""
Preview the site locally with auto-updating photos.

    python serve.py      (or double-click start.bat)

Runs the site at http://localhost:8080 and watches photos/ - drop photos into
a folder, then refresh the page.
"""
import functools
import http.server
import threading
import webbrowser
from pathlib import Path

import update_photos
# The YouTube list is refreshed daily by GitHub (.github/workflows), so it
# isn't refreshed here - that would clash when syncing. Run
# `python update_videos.py` by hand if you want a fresh list locally.

ROOT = Path(__file__).parent
PORT = 8080


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):  # keep the window quiet
        pass


threading.Thread(target=update_photos.watch, daemon=True).start()
handler = functools.partial(NoCacheHandler, directory=str(ROOT))
server = http.server.ThreadingHTTPServer(("localhost", PORT), handler)
print(f"Site running at http://localhost:{PORT}")
if __name__ == "__main__" and "--no-browser" not in __import__("sys").argv:
    webbrowser.open(f"http://localhost:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
