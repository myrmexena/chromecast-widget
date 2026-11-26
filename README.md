# chromecast-widget

Petit widget web local pour piloter un Chromecast depuis l'ordinateur :

1. voir ce qui est en cours de diffusion
2. avancer / reculer de 30 s
3. pause / lecture
4. arrêter la diffusion

## Mini-app macOS (Spotlight)

```bash
./make_app.sh
```

Crée `~/Applications/Chromecast Widget.app` (fenêtre flottante avec l'interface web).
Lancez-la ensuite via Spotlight (⌘ Espace → « Chromecast Widget »).

Menu **Affichage → Passer en mode barre de menus** pour basculer en icône de barre de menus ;
**Ouvrir la fenêtre** dans ce menu revient à la fenêtre. Le dernier mode est mémorisé
(`~/.chromecast-widget.json`).

## Widget barre de menus macOS

```bash
python menubar.py
```

Une icône 📺 apparaît dans la barre de menus (▶️ / ⏸ selon l'état) : titre en cours,
position, ⏪ 30 s, pause/lecture, ⏩ 30 s, arrêt, choix de l'appareil.

## Version page web


```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Puis ouvrir http://127.0.0.1:8765 (ordinateur et Chromecast sur le même réseau).
Sur macOS, autoriser l'accès au réseau local pour le terminal si nécessaire.
