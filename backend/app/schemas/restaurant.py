from pydantic import BaseModel
from list import List


class RestaurantBase(BaseModel):
    id: int
    name: str
    address: str
    cuisine_type : str
    rating: float
    is_open: bool
    phone_number: str
    
class RestaurantCreate(RestaurantBase):
    id: int
    name: str
    address: str
    phone_number: str

class RestaurantUpdate(RestaurantBase):
    id: int
    name: str
    address: str
    phone_number: str



    

