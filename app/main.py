from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
app = FastAPI()

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # Force connection on a request as the connect=True parameter of MongoClient seems to be useless here
    print("\033[94mDATABASE: Connected to MongoDB successfully!\033[0m")
except Exception as e:
    print(f"\033[91mDATABASE: Failed to connect to MongoDB: {e}\033[0m")

@app.get("/")
def read_root():
    return {"message": "API ONLINE!"}