"""Chromecast widget: tiny local web server controlling a Chromecast."""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pychromecast

STATIC = Path(__file__).parent / "static"
PORT = 8765

casts = {}  # friendly name -> Chromecast


def get_cast(name):
    cast = casts.get(name) if name else next(iter(casts.values()), None)
    if cast is None:
        raise LookupError("Aucun Chromecast trouvé")
    cast.wait(timeout=10)
    return cast


def status(cast):
    mc = cast.media_controller
    mc.update_status()
    s = mc.status
    return {
        "device": cast.cast_info.friendly_name,
        "app": cast.status.display_name if cast.status else None,
        "title": s.title,
        "artist": s.artist,
        "image": s.images[0].url if s.images else None,
        "state": s.player_state,
        "current": s.adjusted_current_time,
        "duration": s.duration,
        "volume": cast.status.volume_level if cast.status else None,
        "muted": cast.status.volume_muted if cast.status else None,
    }


def act(cast, action, delta=0.0, level=None):
    mc = cast.media_controller
    mc.update_status()
    if action == "toggle":
        mc.pause() if mc.status.player_state == "PLAYING" else mc.play()
    elif action == "seek":
        target = max(0, (mc.status.adjusted_current_time or 0) + delta)
        if mc.status.duration:
            target = min(target, mc.status.duration)
        mc.seek(target)
    elif action == "stop":
        cast.quit_app()
    elif action == "volume":
        cast.set_volume(min(1.0, max(0.0, level)))
    elif action == "mute":
        cast.set_volume_muted(not cast.status.volume_muted)
    else:
        raise ValueError(f"Action inconnue: {action}")


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_api(self, method):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/api/devices" and method == "GET":
                return self._json(sorted(casts))
            cast = get_cast(q.get("device"))
            if url.path == "/api/status" and method == "GET":
                return self._json(status(cast))
            if url.path == "/api/action" and method == "POST":
                act(cast, q["action"], float(q.get("delta", 0)),
                    float(q["level"]) if "level" in q else None)
                return self._json({"ok": True})
            self._json({"error": "not found"}, 404)
        except LookupError as e:
            self._json({"error": str(e)}, 404)
        except Exception as e:  # noqa: BLE001
            self._json({"error": str(e)}, 500)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._handle_api("GET")
        body = (STATIC / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self._handle_api("POST")

    def log_message(self, *_):
        pass


def main():
    found, br = pychromecast.get_chromecasts()
    casts.update({c.cast_info.friendly_name: c for c in found})
    print(f"Chromecasts: {', '.join(casts) or 'aucun'}")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Widget sur http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        br.stop_discovery()
        sys.exit(0)


if __name__ == "__main__":
    main()
