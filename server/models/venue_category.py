from pydantic import Field
from fastapi import HTTPException, status

from fastapi.encoders import jsonable_encoder
from server.schemas_new.venuecategory import AddVenueCategorySchema
from server.db.utils import get_json_data_from_list

from . import BaseModel

collection_name = "VenueCategories"


class VenueCategory(BaseModel):
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


async def get_total_venuecategory_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def add_new_venuecategory(db, venuecategory: AddVenueCategorySchema):
    ins = VenueCategory(
        name=venuecategory.name, display_name=venuecategory.display_name, image=venuecategory.image)
    await db[collection_name].insert_one(jsonable_encoder(ins))
    new_venuecategory = await find_venuecategory_by_id(db, str(ins.id))
    return new_venuecategory


async def find_venuecategory_by_id(db, id):
    venuecategory = await db[collection_name].find_one({"_id": id})
    if venuecategory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"venuecategory not found!")
    return venuecategory


async def delete_venuecategory_by_id(db, id):
    deleted_venuecategory = await db[collection_name].delete_one({'_id': id})
    if deleted_venuecategory.deleted_count == 1:
        return {f"Successfully deleted venuecategory with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"venuecategory not found!")


async def find_all_venuecategorys(db, page, limit):
    venuecategorys = await db[collection_name].find().skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    return venuecategorys


# async def update_venuecategory(db,id,data):
#     venuecategory

async def check_venuecategory_exists(id,db):  
    venuecategory = await db[collection_name].find_one({"_id": id})
    return venuecategory!=None

async def check_venuecategory_exists(id,db):  
    instrument = await db[collection_name].find_one({"_id": id})
    return instrument!=None