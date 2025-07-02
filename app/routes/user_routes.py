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
        user_dict = user.model_dump()
        print(user_dict)
        if (user_dict.get("username") is None or
            user_dict.get("password") is None or
            user_dict.get("email") is None):
            return JSONResponse(content={"message": "Username, password, and email are required"}, status_code=400)
        if(user_collection.find_one({"username": user_dict["username"]})):
            return JSONResponse(content={"message": "Username already exists"}, status_code=400)
        if(user_collection.find_one({"email": user_dict["email"]})):
            return JSONResponse(content={"message": "Email already exists"}, status_code=400)
        # Encrypt the password
        result = user_collection.insert_one(user_dict)
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to insert user into database")
        # Add the ID from the database insertion to user dict
        user_dict = user.model_dump(exclude={"password", "salt"})
        user_dict["id"] = str(result.inserted_id)
        
        return JSONResponse(content={"message": "User created", "user": user_dict}, status_code=201)        
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")
    
@router.get("/{user_id}", response_model_exclude={"salt"})
def get_user(user_id: str):
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return JSONResponse(content={"user": user}, status_code=200)
    except Exception as e:
        logging.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user")