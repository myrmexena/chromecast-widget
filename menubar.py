"""Chromecast widget: app de barre de menus macOS."""
import threading

import pychromecast
import rumps


class CastWidget(rumps.App):
    def __init__(self):
        super().__init__("📺", quit_button=None)
        self.casts = {}
        self.current = None  # friendly name
        self.now = rumps.MenuItem("Recherche des Chromecast…")
        self.sub = rumps.MenuItem("")
        self.pos = rumps.MenuItem("")
        self.back = rumps.MenuItem("⏪ Reculer de 30 s", callback=lambda _: self.act("seek", -30))
        self.toggle = rumps.MenuItem("⏯ Pause / lecture", callback=lambda _: self.act("toggle"))
        self.fwd = rumps.MenuItem("⏩ Avancer de 30 s", callback=lambda _: self.act("seek", 30))
        self.stop = rumps.MenuItem("⏹ Arrêter la diffusion", callback=lambda _: self.act("stop"))
        self.devices = rumps.MenuItem("Appareil")
        self.menu = [
            self.now, self.sub, self.pos, None,
            self.back, self.toggle, self.fwd, self.stop, None,
            self.devices, rumps.MenuItem("Quitter", callback=rumps.quit_application),
        ]
        threading.Thread(target=self.discover, daemon=True).start()

    def discover(self):
        found, browser = pychromecast.get_chromecasts()
        self._browser = browser  # garde la découverte vivante
        self.casts = {c.cast_info.friendly_name: c for c in found}
        for name in sorted(self.casts):
            self.devices.add(rumps.MenuItem(name, callback=self.select))
        if self.casts:
            self.current = sorted(self.casts)[0]

    def select(self, item):
        self.current = item.title

    def cast(self):
        c = self.casts.get(self.current)
        if c:
            c.wait(timeout=5)
        return c

    def act(self, action, delta=0):
        c = self.cast()
        if not c:
            return
        mc = c.media_controller
        mc.update_status()
        s = mc.status
        if action == "toggle":
            mc.pause() if s.player_state == "PLAYING" else mc.play()
        elif action == "seek":
            target = max(0, (s.adjusted_current_time or 0) + delta)
            if s.duration:
                target = min(target, s.duration)
            mc.seek(target)
        elif action == "stop":
            c.quit_app()

    @rumps.timer(3)
    def refresh(self, _):
        if not self.casts:
            return
        try:
            c = self.cast()
            mc = c.media_controller
            mc.update_status()
            s = mc.status
        except Exception as e:  # noqa: BLE001
            self.now.title = f"Erreur : {e}"
            return
        if s.player_state in (None, "UNKNOWN", "IDLE") and not s.title:
            self.now.title = f"{self.current} : rien en cours"
            self.sub.title = self.pos.title = ""
            self.title = "📺"
            return
        icon = "▶️" if s.player_state == "PLAYING" else "⏸"
        self.title = icon
        self.now.title = s.title or (c.status.display_name if c.status else "En cours")
        self.sub.title = " · ".join(x for x in (s.artist, c.status.display_name if c.status else None) if x)
        self.pos.title = f"{fmt(s.adjusted_current_time)} / {fmt(s.duration)}"


def fmt(sec):
    sec = int(sec or 0)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


if __name__ == "__main__":
    CastWidget().run()
