from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from server.routers import   venues, cart, orders, artist, packages
from server.routers_new import used_products,repair,grow,ads,orders,user,auth, instruments,cart, genres, bands, user as userv2, artist, venue,venue_category, product_category, products
from motor.motor_asyncio import AsyncIOMotorClient
from tempfile import NamedTemporaryFile
from starlette.middleware.cors import CORSMiddleware
from server.db import get_database
import json



app = FastAPI(
    title="Music server",
    description="You are currently seeing backend of music products ecommerce app.",
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

# connection_string = "mongodb+srv://SishirW:JAkJaCmAPcxLoZn8@music.ohrew.mongodb.net/?retryWrites=true&w=majority"
# connection_string = "mongodb://0.0.0.0:27017"
connection_string = "mongodb://localhost:27017"
#connection_string = "mongodb+srv://musecstacy:Zmkh0XoXKIeBgAoI@cluster0.pdfd9si.mongodb.net"
# connection_string = "mongodb+srv://user:LAAAPFukxhKyQoHq@music-app.lnlw82c.mongodb.net/test"


@app.on_event("startup")
async def start_database():
    app.mongodb_client = AsyncIOMotorClient(connection_string)
    app.mongodb = app.mongodb_client["music2"]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(used_products.router)
app.include_router(repair.router)

app.include_router(grow.router)
app.include_router(ads.router)

app.include_router(orders.router)
app.include_router(products.router)

app.include_router(product_category.router)
app.include_router(cart.router)
# For band
app.include_router(bands.router)
app.include_router(instruments.router)
app.include_router(genres.router)
#Venue
app.include_router(venue.router)
app.include_router(venue_category.router)
# # For Authentication
app.include_router(auth.router)
# Users
app.include_router(user.router)
app.include_router(artist.router)
# Products and Repairs

# app.include_router(musical_products.router)
#app.include_router(venues.router)
# Orders
app.include_router(cart.router)
app.include_router(orders.router)

# Ads
#app.include_router(ads.router)

# app.include_router(packages.router)

# app.include_router(userv2.router)
# app.include_router(artist.router)
# app.include_router(venue.router)

@app.get("/")
async def root():
    return {"Welcome": "Welcome to Music app"}

async def save_mongodb_data_to_file(request):

    db = get_database(request)
    collection = db['Artist']
    
    cursor = collection.find()
    data = [document async for document in cursor]
    
    # Create a temporary JSON file
    with NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp_file:
        json.dump(data, temp_file, default=str)

    return temp_file.name

@app.get("/download")
async def download_all_from_mongodb(request: Request):
    json_file_path = await save_mongodb_data_to_file(request)
    return FileResponse(json_file_path, media_type="application/json")



@app.get("/media/{path}/{id}")
async def get_media(id: str, path: str):
    return FileResponse(f'media/{path}/{id}')

@app.get("/media_new/product/{path}/{id}")
async def get_product_media(id: str, path: str):
    return FileResponse(f'media_new/product/{path}/{id}')

@app.get("/media_new/venue/{path}/{id}")
async def get_venue_media(id: str, path: str):
    return FileResponse(f'media_new/venue/{path}/{id}')

@app.get("/media_new/artist/{path}/{id}")
async def get_artist_media(id: str, path: str):
    return FileResponse(f'media_new/artist/{path}/{id}')
@app.get("/media_new/advertisments/{id}")
async def get_advertisments_media(id: str):
    return FileResponse(f'media_new/advertisments/{id}')

@app.get("/media_new/repair/{path}/{id}")
async def get_repair_media(id: str, path: str):
    return FileResponse(f'media_new/repair/{path}/{id}')