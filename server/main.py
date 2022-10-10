from fastapi import FastAPI
from fastapi.responses import FileResponse
from server.routers import musical_products,user,auth,venues,cart
from motor.motor_asyncio import AsyncIOMotorClient
from . import models
#from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware



# from .database import SessionLocal, engine
# models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Music server",
     description= "You are currently seeing backend of music products ecommerce app.",
     version="0.0.1",
     )

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:49508"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

connection_string="mongodb+srv://SishirW:JAkJaCmAPcxLoZn8@music.ohrew.mongodb.net/?retryWrites=true&w=majority"
#connection_string="mongodb://localhost:27017"


@app.on_event("startup")
async def start_database():
    app.mongodb_client = AsyncIOMotorClient(connection_string)
    app.mongodb = app.mongodb_client["music"]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(musical_products.router)
app.include_router(cart.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(venues.router)

@app.get("/")
async def root():
    return {"Welcome": "Welcome to Music app"}

@app.get("/media/{path}/{id}")
async def get_media(id: str,path:str):
    return FileResponse(f'media/{path}/{id}')
