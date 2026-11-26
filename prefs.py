"""Mode d'affichage (fenêtre / barre de menus) mémorisé entre deux lancements."""
import json
import subprocess
import sys
from pathlib import Path

FILE = Path.home() / ".chromecast-widget.json"
APP = Path(__file__).parent / "app.py"


def get_mode():
    try:
        return json.loads(FILE.read_text()).get("mode", "window")
    except Exception:  # noqa: BLE001
        return "window"


def set_mode(mode):
    FILE.write_text(json.dumps({"mode": mode}))


def relaunch():
    """Démarre une nouvelle instance détachée (appelée quand l'ancienne se ferme)."""
    subprocess.Popen([sys.executable, str(APP)], cwd=APP.parent,
                     start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
