from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models import User
from cryptography.fernet import Fernet
from bson import ObjectId
import logging
from app.database import client

db = client.get_database()
user_collection = db.users

router = APIRouter()

@router.post("/create/", response_model_exclude={"salt"})
def create_user(user : User):
    try:
        print(user)
        user_dict = user.model_dump()
        result = user_collection.insert_one(user_dict)
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to insert user into database")
        return JSONResponse(content={"message": "User created"}, status_code=201)
        
        
        return "User created"
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")