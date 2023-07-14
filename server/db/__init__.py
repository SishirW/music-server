from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient


def get_database(request: Request) -> AsyncIOMotorClient:
    return request.app.mongodb
