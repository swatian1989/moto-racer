"""
Musa Moto Racer - Coastline : desktop launcher.

Serves the game from a local HTTP server and shows it in a native window.
It has to be HTTP rather than file:// because a service worker (and therefore
offline play, and a few storage APIs) will not run from a file:// origin.

Two details matter for a game that keeps progress:

  * The port is fixed. localStorage is keyed by origin, and the origin
    includes the port, so a port that moved between launches would look like
    a brand new machine every time and wipe the garage.
  * private_mode=False with an explicit storage_path, otherwise WebView2
    hands us a throwaway profile and progress vanishes on exit.
"""

import argparse
import http.server
import os
import socket
import socketserver
import sys
import threading
import urllib.request
import webbrowser

APP_NAME = "Musa Moto Racer"
# Chosen to sit in the dynamic/private range and be unlikely to clash.
# Changing it in a later release would orphan the player's saved progress.
DEFAULT_PORT = 47821
PORT_ATTEMPTS = 8


def game_dir():
    """Where the web assets live, bundled or running from source."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    bundled = os.path.join(base, "game")
    if os.path.isdir(bundled):
        return bundled
    # running from the repo: desktop/ sits next to index.html
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=game_dir(), **kw)

    def end_headers(self):
        # The service worker caches for us; letting the browser cache on top
        # only makes a reinstalled build serve yesterday's game.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


# Python's default map misses a couple of these on some Windows installs,
# and a wrong type on the manifest or the worker breaks installability.
Handler.extensions_map.update({
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".json": "application/json",
    ".webmanifest": "application/manifest+json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".html": "text/html",
})


def already_ours(port):
    """True if something on this port is a running copy of this app."""
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:%d/manifest.json" % port, timeout=1.5
        ) as r:
            return b"Musa Moto Racer" in r.read(400)
    except Exception:
        return False


def start_server(preferred):
    """Return (port, httpd|None). httpd is None when reusing a live instance."""
    last = None
    for port in range(preferred, preferred + PORT_ATTEMPTS):
        try:
            socketserver.TCPServer.allow_reuse_address = False
            httpd = socketserver.TCPServer(("127.0.0.1", port), Handler)
        except OSError as e:
            last = e
            if already_ours(port):
                return port, None          # second launch: reuse instance one
            continue
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        return port, httpd
    raise SystemExit("Could not open a local port for %s (%s)" % (APP_NAME, last))


def storage_path():
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(root, "MotoRacer", "webview")
    os.makedirs(path, exist_ok=True)
    return path


def open_in_browser(url):
    """Fallback: a Chromium app window, or failing that the default browser."""
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome",
                     "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome",
                     "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge",
                     "Application", "msedge.exe"),
    ]
    for exe in candidates:
        if exe and os.path.exists(exe):
            import subprocess
            subprocess.Popen([exe, "--app=" + url,
                              "--user-data-dir=" + os.path.join(storage_path(), "chromium")])
            return True
    return webbrowser.open(url)


class QuitApi:
    """Exposed to the page as window.pywebview.api.

    The game's EXIT button needs to close the *application*, not just the
    page: a fullscreen window with no browser chrome otherwise has no way
    out at all. The page feature-detects this object to tell a desktop
    build apart from a browser tab.
    """

    def __init__(self, window=None):
        self.window = window

    def quit(self):
        if self.window is not None:
            self.window.destroy()
        return True


def keep_alive_window(url):
    """The browser fallback leaves nothing on screen owning the process, and a
    windowless build would have no way to quit short of Task Manager."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title(APP_NAME)
        root.geometry("380x150")
        root.configure(bg="#1a1230")
        tk.Label(root, text="%s is running" % APP_NAME, bg="#1a1230", fg="#ffd23a",
                 font=("Segoe UI", 13, "bold")).pack(pady=(22, 6))
        tk.Label(root, text=url, bg="#1a1230", fg="#ffe6cf",
                 font=("Consolas", 10)).pack()
        tk.Button(root, text="Quit", width=14, command=root.destroy).pack(pady=16)
        root.mainloop()
    except Exception:
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass


def main():
    ap = argparse.ArgumentParser(description="%s desktop launcher" % APP_NAME)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT,
                    help="local port to serve on (default %d)" % DEFAULT_PORT)
    ap.add_argument("--serve-only", action="store_true",
                    help="run the server without opening a window")
    ap.add_argument("--browser", action="store_true",
                    help="open in your browser instead of the app window")
    args = ap.parse_args()

    port, httpd = start_server(args.port)
    url = "http://127.0.0.1:%d/" % port

    if args.serve_only:
        print("%s serving at %s  (Ctrl+C to stop)" % (APP_NAME, url))
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        return

    if httpd is None:
        # An instance is already serving; just show a window onto it.
        pass

    if not args.browser:
        try:
            import webview
            api = QuitApi()
            api.window = webview.create_window(
                APP_NAME, url, width=1000, height=680,
                min_size=(420, 560), resizable=True, js_api=api,
            )
            webview.start(private_mode=False, storage_path=storage_path())
            return
        except Exception as e:
            print("Native window unavailable (%s); falling back to a browser." % e)

    open_in_browser(url)
    keep_alive_window(url)


if __name__ == "__main__":
    main()
