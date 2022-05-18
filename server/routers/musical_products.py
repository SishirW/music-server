from fastapi import APIRouter, HTTPException, Depends, UploadFile
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, database, models
import shutil
from uuid import uuid1
get_db= database.get_db

router= APIRouter(prefix= "/products",tags=["Musical products"])

@router.post("/")
async def create_product(file: UploadFile, request: schemas.CreateProduct= Depends(), db: Session= Depends(get_db)):
    new_product= models.Products(name= request.name, price= request.price, seller= request.seller, description= request.description)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    image_name= uuid1()
    with open(f"media/{image_name}.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    new_image= models.Images(name= f"{image_name}.png", url= f"/media/{image_name}.png", parent_id=db.query(models.Products).filter(models.Products.name== request.name).first().id)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return {f"Successfully created a {request.name} product"}


@router.get("/", response_model=List[schemas.Product])
async def get_products(db: Session= Depends(get_db)):
    return db.query(models.Products).all()

@router.get("/{id}")
async def get_product(id: int,db: Session= Depends(get_db)):
    product= db.query(models.Products).filter(models.Products.id==id).first()
    if product is None: 
        raise HTTPException(404, detail= f"Product with id {id} not found")
    return product

@router.get('/images')
async def get_images(db : Session= Depends(get_db)):
    return db.query(models.Images).all()