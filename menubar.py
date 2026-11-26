"""Chromecast widget: app de barre de menus macOS."""
import threading

import pychromecast
import rumps
import zeroconf
from pychromecast.discovery import CastBrowser, SimpleCastListener


class CastWidget(rumps.App):
    def __init__(self):
        super().__init__("📺", quit_button=None)
        self.casts = {}
        self.current = None  # friendly name
        self.now = rumps.MenuItem("Recherche des Chromecast…")
        self.infos = {}
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
        """Découverte continue : met à jour self.infos quand un appareil apparaît/disparaît."""
        self.zc = zeroconf.Zeroconf()
        self.infos = {}  # uuid -> CastInfo

        def sync(uuid, _service=None):
            info = self._browser.devices.get(uuid)
            if info:
                self.infos[uuid] = info

        def remove(uuid, _service, _info):
            self.infos.pop(uuid, None)
            for name in [n for n, c in self.casts.items() if c.uuid == uuid]:
                self.casts.pop(name).disconnect()

        self._browser = CastBrowser(SimpleCastListener(sync, remove, sync), self.zc)
        self._browser.start_discovery()

    def sync_devices(self):
        """Appelé depuis le thread principal : reflète les appareils et l'icône."""
        for uuid, info in list(self.infos.items()):
            if info.friendly_name not in self.casts:
                self.casts[info.friendly_name] = pychromecast.get_chromecast_from_cast_info(info, self.zc)
        names = sorted(self.casts)
        if names != getattr(self, "_names", None):
            self._names = names
            if self.devices._menu is not None:
                self.devices.clear()
            for name in names:
                self.devices.add(rumps.MenuItem(name, callback=self.select))
            if self.current not in self.casts:
                self.current = names[0] if names else None
        # icône visible seulement si au moins un Chromecast est sur le réseau
        item = self._nsapp.nsstatusitem
        if hasattr(item, "setVisible_"):
            item.setVisible_(bool(names))

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
        self.sync_devices()
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
