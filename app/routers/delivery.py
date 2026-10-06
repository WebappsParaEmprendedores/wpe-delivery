from fastapi import APIRouter, Depends
from pymongo.database import Database as PyMongoDatabase

from app.db.database import mongo_db_dependency
from app.auth.bearer import verify_bearer_token
from app.models.delivery import DeliveryUpdate
from app.services import delivery

router = APIRouter(
	prefix='/d',
	tags=['Deliveries'],
	dependencies=[Depends(verify_bearer_token)],
)

# there's some problems with models and mongo, avoid using 'response_model'
@router.get('/daily/{delivery_date}/{driver_code}')
def get_daily(delivery_date: str, driver_code: str, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	return delivery.get_daily(delivery_date, driver_code, db)


@router.get('/marker/{hash}')
def get_delivery_by_hash(hash: str, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	return delivery.get_delivery_by_hash(hash, db)


@router.put('/marker/{hash}')
def update_localization(hash: str, posted_data: DeliveryUpdate, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	return delivery.update_localization(hash, posted_data, db)




"""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException


@router.patch("/{delivery_id}")
def update_delivery(delivery_id: str, data: DeliveryUpdate):
	try:
		object_id = ObjectId(delivery_id)
	except InvalidId:
		raise HTTPException(
			status_code=400,
			detail="Invalid MongoDB ObjectId",
		)

	changes = data.model_dump(exclude_unset=True)

	result = db["deliveries"].update_one(
		{"_id": object_id},
		{"$set": changes},
	)

	if result.matched_count == 0:
		raise HTTPException(
			status_code=404,
			detail="Delivery not found",
		)

	return {
		"message": "Delivery updated successfully",
		"_id": delivery_id,
	}

"""