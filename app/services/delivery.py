from datetime import datetime
from fastapi import HTTPException, status
from pymongo import ReturnDocument, DESCENDING
from pymongo.database import Database

from app.models.delivery import DeliveryUpdate

deliveryResponse = {
	"_id": 0,
	#"delivery_date": 0,
	#"driver_code": 0,
	"created_at": 0,
	"updated_at": 0,
}


def get_daily(delivery_date: str, driver_code: str, db: Database):
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

def get_delivery_by_hash(hash: str, db: Database):
	delivery = __getByHash(hash, db)

	if delivery is None:
		raise HTTPException(
			status_code=404,
			detail="Record not found",
		)

	return delivery

def update_localization(hash: str, posted_data: DeliveryUpdate, db: Database):
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
			sort=[ # updates starting from the last registered
				("created_at", DESCENDING),
				("_id", DESCENDING),
			],
			return_document=ReturnDocument.AFTER,
		)

		return updated_delivery
	except:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record not found')


# privates
def __getByHash(hash:str, db:Database):
	return db["deliveries"].find_one(
		{"hash": hash},
		deliveryResponse,
	)


###