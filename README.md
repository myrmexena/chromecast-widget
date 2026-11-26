# chromecast-widget

Petit widget web local pour piloter un Chromecast depuis l'ordinateur :

1. voir ce qui est en cours de diffusion
2. avancer / reculer de 30 s
3. pause / lecture
4. arrêter la diffusion

## Lancer

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Puis ouvrir http://127.0.0.1:8765 (ordinateur et Chromecast sur le même réseau).
Sur macOS, autoriser l'accès au réseau local pour le terminal si nécessaire.
