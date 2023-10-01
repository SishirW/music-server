from pydantic import Field
from fastapi import HTTPException, status

from fastapi.encoders import jsonable_encoder
from server.schemas_new.productcategory import AddProductCategorySchema
from server.db.utils import get_json_data_from_list

from . import BaseModel

collection_name = "ProductCategories"


class ProductCategory(BaseModel):
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


async def get_total_productcategory_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def add_new_productcategory(db, productcategory: AddProductCategorySchema):
    ins = ProductCategory(
        name=productcategory.name, display_name=productcategory.display_name, image=productcategory.image)
    await db[collection_name].insert_one(jsonable_encoder(ins))
    new_productcategory = await find_productcategory_by_id(db, str(ins.id))
    return new_productcategory


async def find_productcategory_by_id(db, id):
    productcategory = await db[collection_name].find_one({"_id": id})
    if productcategory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"productcategory not found!")
    return productcategory


async def delete_productcategory_by_id(db, id):
    deleted_productcategory = await db[collection_name].delete_one({'_id': id})
    if deleted_productcategory.deleted_count == 1:
        return {f"Successfully deleted productcategory with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"productcategory not found!")


async def find_all_productcategorys(db, page, limit):
    productcategorys = await db[collection_name].find().skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    return productcategorys


# async def update_productcategory(db,id,data):
#     productcategory

async def check_productcategory_exists(id,db):  
    productcategory = await db[collection_name].find_one({"_id": id})
    print(productcategory)
    return productcategory!=None

