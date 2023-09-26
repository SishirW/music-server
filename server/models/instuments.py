from pydantic import Field
from fastapi import HTTPException, status

from fastapi.encoders import jsonable_encoder
from server.schemas_new.instruments import AddInstrumentSchema, UpdateInstrumentSchema
from server.db.utils import get_json_data_from_list

from . import BaseModel

collection_name = "Instruments"


class Instrument(BaseModel):
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


async def get_total_instrument_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def add_new_instrument(db, instrument: AddInstrumentSchema):
    ins = Instrument(
        name=instrument.name, display_name=instrument.display_name, image=instrument.image)
    await db[collection_name].insert_one(jsonable_encoder(ins))
    new_instrument = await find_instrument_by_id(db, str(ins.id))
    return new_instrument


async def find_instrument_by_id(db, id):
    instrument = await db[collection_name].find_one({"_id": id})
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Instrument not found!")
    return instrument


async def delete_instrument_by_id(db, id):
    deleted_instrument = await db[collection_name].delete_one({'_id': id})
    if deleted_instrument.deleted_count == 1:
        return {f"Successfully deleted instrument with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Instrument not found!")


async def find_all_insturments(db, page, limit):
    insturments = await db[collection_name].find().skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    return insturments


# async def update_instrument(db,id,data):
#     instrument

async def check_instrument_exists(id,db):  
    instrument = await db[collection_name].find_one({"_id": id})
    return instrument!=None