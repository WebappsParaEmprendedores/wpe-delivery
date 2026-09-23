from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class DeliveryResponse(BaseModel):
	"""id: PyObjectId | None = Field(
		default=None,
		alias="_id",
		description="MongoDB document identifier",
	)"""
	id: str
	order: str
	addressee: str
	phone: str
	address: str
	latitude: float
	longitude: float
	delivery_date: str
	driver_code: str
	hash: str

	model_config = ConfigDict(
		populate_by_name=True,
		from_attributes=True,
	)

class DeliveryUpdate(BaseModel):
	latitude: float
	longitude: float