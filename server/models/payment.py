from . import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

booking_payment_collection_name= 'BookingTransaction'
order_payment_collection_name= 'ProductTransaction'

class BookingPayment(BaseModel):
    khalti_token: str
    idx: str
    phone: str
    amount: int
    amount_paid_in_rs: int
    package: str
    venue:str
    user_id:str

class OrderPayment(BaseModel):
    khalti_token: str
    idx: str
    phone: str
    amount: int
    amount_paid_in_rs: int
    user_id:str
async def complete_booking_payment(db ,venue,package,payment, user):
    payment= BookingPayment(
        khalti_token=payment.khalti_token,
        idx=payment.idx,
        phone=payment.phone,
        amount=payment.amount,
        amount_paid_in_rs=payment.amount/100,
        package=package,
        venue= venue,
        user_id=user
    )
    await db[booking_payment_collection_name].insert_one(jsonable_encoder(payment))
    payment_detail=await get_booking_payment_by_id(db, str(payment.id))
    return payment_detail

async def get_booking_payment_by_id(db,id):
    payment= await db[booking_payment_collection_name].find_one({"_id": id})
    if payment is None:
        raise HTTPException(status_code=404, detail=f"payment not found")
    return payment


async def complete_order_payment(db ,payment, user):
    payment= OrderPayment(
        khalti_token=payment.khalti_token,
        idx=payment.idx,
        phone=payment.phone,
        amount=payment.amount,
        amount_paid_in_rs=payment.amount/100,
        user_id=user
    )
    await db[order_payment_collection_name].insert_one(jsonable_encoder(payment))
    payment_detail=await get_order_payment_by_id(db, str(payment.id))
    return payment_detail

async def get_order_payment_by_id(db,id):
    payment= await db[order_payment_collection_name].find_one({"_id": id})
    if payment is None:
        raise HTTPException(status_code=404, detail=f"payment not found")
    return payment