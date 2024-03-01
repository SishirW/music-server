from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from server.routers import venues, cart, orders, artist, packages
from server.routers_new import used_products, repair, grow, ads, orders, user, auth, instruments, cart, genres, bands, user as userv2, artist, venue, venue_category, product_category, products
from motor.motor_asyncio import AsyncIOMotorClient
from tempfile import NamedTemporaryFile
from starlette.middleware.cors import CORSMiddleware
from server.db import get_database
import json
from fastapi.responses import HTMLResponse


load_dotenv()

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
#connection_string = "mongodb://localhost:27017"
connection_string = "mongodb+srv://musecstacy:Zmkh0XoXKIeBgAoI@cluster0.pdfd9si.mongodb.net"
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
# Venue
app.include_router(venue.router)
app.include_router(venue_category.router)
# # For Authentication
app.include_router(auth.router)
# Users
app.include_router(user.router)
app.include_router(artist.router)
# Products and Repairs

# app.include_router(musical_products.router)
# app.include_router(venues.router)
# Orders
app.include_router(cart.router)
app.include_router(orders.router)

# Ads
# app.include_router(ads.router)

# app.include_router(packages.router)

# app.include_router(userv2.router)
# app.include_router(artist.router)
# app.include_router(venue.router)


@app.get("/")
async def root():
    return {"Welcome": "Welcome to Music app"}

@app.get("/privacy-policy")
async def privacy_policy():
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy</title>
</head>
<body>
    

    <h2>
        Privacy Policy
    </h2>
<br>

    At Musecstacy, one of our main priorities is the privacy of our visitors and users. This Privacy Policy Page contains information about how Musecstacy collect our user’s data so that we can use it to analyze our visitor’s preferences and give the best experience we can.

Our privacy policy includes what type of information we collect, why we collect it, and how we use the information to give the best service to our users. This policy does not apply to any information collected offline or via channels other than this website.

Musecstacy makes sure that we treat our users’ data with respect and do not tend to misuse it.

This Privacy Policy applies to the domain https://meforchange.com.

Depending on your activities while visiting our website, you may be required to agree to additional terms and conditions.


<h3>Consent</h3>
<br>

By using our website or accessing any kinds of services, you hereby consent to our Privacy Policy and agree to its terms.

 
<h3>Website Visitors</h3>

<br>
Musecstacy only collects non-personally-identifying information that is easily available.

It includes information such as the browser name, language preference, country name, referring site, and the date and time of each visitor request.

Musecstacy protects all your personal data. Remember the name you provide on our website is public. So, we advise you to choose carefully about what you want to display on your profile. Except that we do not publish your email and any other information publicly that may be crucial.

 <h3>Collection of Personally-Identifying Information
</h3>
<br>

Some visitors to Musecstacy website choose to interact with Musecstacy in a way that requires personally identifying information.

For example, visitors may have to enter his/her email address to comment on the products.

Musecstacy takes all measures reasonably necessary to protect against the unauthorized access, use, alteration, or destruction of potentially personally identifying information.

<h3>Why do we collect your data?</h3>
<br>


Musecstacy’s purpose in collecting non-personally identifying information is to better understand how Musecstacys visitors use its website thus providing our users with more quality content according to their interests.

Likewise, Musecstacys may also release non-personally-identifying information in the aggregate, e.g., by publishing a report on trends in the usage of its website.

 
<h3>How we use your information</h3>
<br>

We use the information we collect in various ways, including to:

Provide, operate, and maintain our website

Improve, personalize, and expand our website

Analyze user’s trends and patterns

Develop new products, services, features, and functionality

Communicate with you, either directly or through one of our partners, including for customer service, to provide you with updates and other information relating to the website, and for marketing and promotional purposes

Understand and analyze how you use our app

Send you emails if necessary.

<h3>Reporting data breaches</h3>
<br>

If by any means, data of Musecstacy is breached that may affect our users and hamper their rights to information, we make sure that our users are informed.







<h3>Out-going Links</h3>
<br>

Musecstacy’ content may contain links to other websites. We are not responsible for the privacy policies of such websites and how they use your information.

 
<h3>Comments</h3>


Any comment you do on our website becomes public information. So please be cautious when posting the comments on our website and do not display any personal information.

 
<h3>Parental Guidelines</h3>
<br>

Musecstacy are not intended to be used by children. So, we advise parents to not allow their children to use on their own and closely monitor them while using our service.

Musecstacy are not responsible for any activities performed by our users being influenced by our content.




<h3>GDPR Data Protection Rights</h3>
<br>

Under the GDPR data protection rights, the Musecstacy team would like to make sure that our users are aware of the data we have collected.

The right to accessing the data – Our users have full right to request a copy of the data that we have stored and request to delete.

The right to consent – Users have the full right to allow or disallow us to access their data. We will access your data with your consent.

The right to data breaches information – We are obliged to alert our users in case of any data breaches happened.

The right to data portability – Our users have full right to move their data from our service.

Right as independent – We keep our user’s information like location, device identifiers, and Ip address as personal data.

If you make a request, we have one month to respond to you. If you would like to exercise any of these rights, please contact us.

 
<h3>Privacy Policy Changes</h3>
<br>

Musecstacy’s might require to change privacy policy frequently according to the requirements. So, we encourage our users to visit this privacy policy page.

Your continuation to visit the website at any time gives information about your acceptance of our privacy policy.

 
<h3>Contact Us</h3>
<br>

If you have any queries regarding our privacy policy, you are welcome to contact us on the information.


</body>
</html>
    """
    return HTMLResponse(content=html_content, status_code=200)



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


@app.get("/media_new/used_product/{path}/{id}")
async def get_repair_media(id: str, path: str):
    return FileResponse(f'media_new/used_product/{path}/{id}')
