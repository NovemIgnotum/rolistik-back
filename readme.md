Pour lancer le projet
python -m uvicorn main:app --reload
OU
./start.sh

Pour lancer les tests
PYTHONPATH=$(pwd) pytest
