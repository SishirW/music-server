from pydantic import Field
from fastapi import HTTPException, status

from fastapi.encoders import jsonable_encoder
from server.schemas_new.genres import AddGenreSchema
from server.db.utils import get_json_data_from_list

from . import BaseModel

collection_name = "Genres"


class Genre(BaseModel):
    name: str = Field(str)
    display_name: str = Field(str)
    image: str = Field(str)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": "guitar",
                "display_name": "Guitar",
                "image": "",
            }
        }


async def get_total_genre_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def add_new_genre(db, genre: AddGenreSchema):
    ins = Genre(
        name=genre.name, display_name=genre.display_name, image=genre.image)
    await db[collection_name].insert_one(jsonable_encoder(ins))
    new_genre = await find_genre_by_id(db, str(ins.id))
    return new_genre


async def find_genre_by_id(db, id):
    genre = await db[collection_name].find_one({"_id": id})
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"genre not found!")
    return genre


async def delete_genre_by_id(db, id):
    deleted_genre = await db[collection_name].delete_one({'_id': id})
    if deleted_genre.deleted_count == 1:
        return {f"Successfully deleted genre with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"genre not found!")


async def find_all_genres(db, page, limit):
    genres = await db[collection_name].find().skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    return genres


# async def update_genre(db,id,data):
#     genre
