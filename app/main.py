from fastapi import FastAPI
from .routes import user_router
app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["user"])

@app.get("/")
async def read_root():
    return {"message": "API online"}