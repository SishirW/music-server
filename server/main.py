from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from server.routers import musical_products
from . import models


from .database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(musical_products.router)

@app.get("/")
async def root():
    return {"Welcome": "Welcome to Music app"}

@app.get("/media/{id}")
async def get_media(id: str):
    return FileResponse(f'media/{id}')
