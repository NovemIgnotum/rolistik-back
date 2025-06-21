from .config import settings
from pymongo import MongoClient

# Connexion à MongoDB avec l'URL définie dans les variables d'environnement
client = MongoClient(settings.DATABASE_URL)