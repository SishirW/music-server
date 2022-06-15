from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from server.routers import musical_products
from motor.motor_asyncio import AsyncIOMotorClient
from . import models


# from .database import SessionLocal, engine
# models.Base.metadata.create_all(bind=engine)


app = FastAPI()
@app.on_event("startup")
async def start_database():
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client["music"]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(musical_products.router)

@app.get("/")
async def root():
    return {"Welcome": "Welcome to Music app"}

@app.get("/media/{id}")
async def get_media(id: str):
    return FileResponse(f'media/{id}')
