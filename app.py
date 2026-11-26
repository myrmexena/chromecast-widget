"""Chromecast Widget : mini-app macOS (fenêtre native affichant la page web)."""
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pychromecast
import webview
import zeroconf
from pychromecast.discovery import CastBrowser, SimpleCastListener

import server

ICON = Path(__file__).parent / "assets" / "AppIcon.icns"


def start_discovery():
    """Découverte continue : les appareils apparaissent/disparaissent dans server.casts."""
    zc = zeroconf.Zeroconf()
    holder = {}

    def add(uuid, _service=None):
        info = holder["b"].devices.get(uuid)
        if info:
            server.casts[info.friendly_name] = pychromecast.get_chromecast_from_cast_info(info, zc)

    def remove(uuid, _service, info):
        server.casts.pop(info.friendly_name, None)

    holder["b"] = CastBrowser(SimpleCastListener(add, remove, add), zc)
    holder["b"].start_discovery()
    return holder["b"]


def brand_app():
    """Nom et icône du Dock (le process est un Python générique)."""
    try:
        from AppKit import NSApplication, NSBundle, NSImage
        info = NSBundle.mainBundle().infoDictionary()
        info["CFBundleName"] = "Chromecast Widget"
        if ICON.exists():
            NSApplication.sharedApplication().setApplicationIconImage_(
                NSImage.alloc().initWithContentsOfFile_(str(ICON)))
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("127.0.0.1", server.PORT), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    browser = start_discovery()
    webview.create_window(
        "Chromecast", f"http://127.0.0.1:{server.PORT}",
        width=380, height=390, resizable=False, on_top=True,
    )
    webview.start(brand_app)
    browser.stop_discovery()
