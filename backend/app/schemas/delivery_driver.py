from pydantic import BaseModel
from app.schemas.user import User

class DeliveryDriver(User):
    current_location: str
    vehicle_info: str
    is_active: bool