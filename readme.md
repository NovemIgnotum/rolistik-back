# Rolistik-back

Backend de l'application Rolistik, développé avec [FastAPI](https://fastapi.tiangolo.com/).

## Installation

```bash
git clone https://github.com/NovemIgnotum/rolistik-back.git
cd rolistik-back
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lancement du serveur

```bash
uvicorn main:app --reload
```

## Structure du projet

- `main.py` : Point d'entrée de l'application FastAPI.
- `app/` : Modules et routes de l'application.
- `test/` : Modules des tests unitaires
- `requirements.txt` : Dépendances Python.

## Documentation API

Une fois le serveur lancé, la documentation interactive est disponible sur :

- Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Tests

```bash
pytest
```

## Licence

MIT
