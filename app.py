"""Chromecast Widget : mini-app macOS (fenêtre native affichant la page web)."""
import threading
from http.server import ThreadingHTTPServer

import pychromecast
import webview

import server


def start_backend():
    found, _browser = pychromecast.get_chromecasts()
    server.casts.update({c.cast_info.friendly_name: c for c in found})


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("127.0.0.1", server.PORT), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    threading.Thread(target=start_backend, daemon=True).start()
    webview.create_window(
        "Chromecast", f"http://127.0.0.1:{server.PORT}",
        width=380, height=330, resizable=False, on_top=True,
    )
    webview.start()
