from pydantic import BaseModel
from typing import List, Optional

#dont have everything in the base model because we want to be able to update only certain fields without having to provide all of them
class RestaurantBase(BaseModel):
    name: str
    address: str
    cuisine_type: str
    phone_number: str
    price_tier: int #for feat3-fr1, im gonna add this for our searching by price tier feature, this will be an integer from 1 to 4, with 1 being the cheapest and 4 being the most expensive

#create and update models inherit from the base model, but the update model has all fields optional so we can update only certain fields without having to provide all of them
class restaurantCreate(RestaurantBase):
    pass
    
#but here we can update only certain fields without having to provide all of them, so we make all fields optional
class RestaurantUpdate(RestaurantBase):
    name: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone_number: Optional[str] = None
    is_open: Optional[bool] = None
    price_tier: Optional[int] = None #added this for the update model as well, so we can update the price tier if we want to

#for reading
class Restaurant(RestaurantBase):
    id: int
    rating: float
    is_open: bool

#this will be for feature 3
class SearchResponse(BaseModel):
    message: str
    data: List[Restaurant]

    

