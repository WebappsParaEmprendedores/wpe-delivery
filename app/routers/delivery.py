from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import ReturnDocument
from pymongo.database import Database as PyMongoDatabase

from app.db.database import mongo_db_dependency
from app.auth.bearer import verify_bearer_token
from app.models.delivery import DeliveryUpdate

deliveryResponse = {
	"_id": 0,
	#"delivery_date": 0,
	#"driver_code": 0,
	"created_at": 0,
	"updated_at": 0,
}

router = APIRouter(
	prefix='/d',
	tags=['Deliveries'],
	dependencies=[Depends(verify_bearer_token)],
)

# there's some problems with models and mongo, avoid using 'response_model'
@router.get('/daily/{delivery_date}/{driver_code}')
def get_daily(delivery_date: str, driver_code: str, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	deliveries = list(db["deliveries"].find(
		{
			'delivery_date': delivery_date,
			'driver_code': driver_code,
		},
		{'_id':0},
	))

	if not deliveries:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No records found!')

	return deliveries


@router.get('/marker/{hash}')
def get_delivery_by_hash(hash: str, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	delivery = __getByHash(hash, db)

	if delivery is None:
		raise HTTPException(
			status_code=404,
			detail="Record not found",
		)

	return delivery

@router.put('/marker/{hash}')
def update_localization(hash: str, posted_data: DeliveryUpdate, db: PyMongoDatabase = Depends(mongo_db_dependency)):
	try:
		updated_delivery = db["deliveries"].find_one_and_update(
			{"hash": hash},
			{
				"$set": {
					"latitude": posted_data.latitude,
					"longitude": posted_data.longitude,
					"localization_updated": True,
					"updated_at": datetime.now(),
				}
			},
			projection=deliveryResponse,
			return_document=ReturnDocument.AFTER,
		)

		return updated_delivery
	except:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record not found')


# privates
def __getByHash(hash:str, db:PyMongoDatabase):
	return db["deliveries"].find_one(
		{"hash": hash},
		deliveryResponse,
	)


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