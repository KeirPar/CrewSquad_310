from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from app.packages.geo.coordinate import Coordinate


#Putting first as was getting errors when not specified first
class CuisineType(str, Enum):
    ITALIAN = "Italian"
    MEXICAN = "Mexican"
    CHINESE = "Chinese"
    GREEK = "Greek"
    JAPANESE = "Japanese"
    AMERICAN = "American"
    INDIAN = "Indian"
    OTHER = "Other"

#dont have everything in the base model because we want to be able to update only certain fields without having to provide all of them
class RestaurantBase(BaseModel):
    name: str
    address: str
    coordinate: Coordinate=Coordinate(49.94290035633633, -119.39555529342739)
    cuisine_type: CuisineType #validated with enum
    phone_number: str
    price_tier: int = Field(..., ge=1, le=4) #for feat3-fr1, im gonna add this for our searching by price tier feature, this will be an integer from 1 to 4, with 1 being the cheapest and 4 being the most expensive
#Edit to the above comment from keir, I updated this to do so in Feat2-FR3

#create and update models inherit from the base model
class restaurantCreate(RestaurantBase):
    pass
    
#but here we can update only certain fields without having to provide all of them, so we make all fields optional
class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[CuisineType] = None
    phone_number: Optional[str] = None
    is_open: Optional[bool] = None
    price_tier: Optional[int] = Field(None, ge=1, le=4) #changed this price tier 
    
#for reading
class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    rating: float = 0.0 #updated this to have a value
    is_open: bool = True #updated this to have a value

#this will be for feature 3
class SearchResponse(BaseModel):
    message: str
    data: List[Restaurant]


