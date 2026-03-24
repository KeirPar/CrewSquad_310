from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from app.packages.geo.coordinate import Coordinate

#Making roles with enforcing of being a Customer or Owner exclusively
class UserRole(str, Enum):
    CUSTOMER = "Customer"
    OWNER = "Restaurant Owner"

#Using basemodel this is what users will be filling out on a creation/registration form
class UserCreate(BaseModel):
    name: str
    email: EmailStr #Refactor to make it auto validate format
    phone_number: str
    password: str = Field(..., min_length=8)
    role: UserRole
    address: str = Field(..., description="Required for US1 delivery history")
    coordinate: Coordinate = Coordinate(49.94290035633633, -119.39555529342739)


#Storing the user data internally
class User(BaseModel):
    id: int
    name: str
    password_hash: str
    email: EmailStr
    phone_number: str
    role: UserRole
    #   TODO: Maybe we should move the address, coordinate to Customer & Restaurant, order_history&cart to Customer, unless all users (RestaurantManager, Admin) needs an address and other properties.
    address: str
    coordinate: Coordinate = Coordinate(49.94290035633633, -119.39555529342739)
    order_history: list[int] = [] #stores order id
    cart: list[int] = [] #stores cart id
