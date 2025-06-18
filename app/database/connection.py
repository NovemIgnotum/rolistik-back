from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    
    @classmethod
    def initialize(cls):
        mongo_uri = os.getenv("MONGO_URI")
        try:
            cls.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            cls.client.server_info()  # Force connection on a request
            print("\033[94mDATABASE: Connected to MongoDB successfully!\033[0m")
            return True
        except Exception as e:
            print(f"\033[91mDATABASE: Failed to connect to MongoDB: {e}\033[0m")
            return False
    
    @classmethod
    def get_client(cls, name):
        return cls.database[name]
    