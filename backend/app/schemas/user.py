from pydantic import BaseModel, EmailStr, Field
from enum import Enum

#Making roles with enforcing of being a Customer or Owner exclusively
class UserRole(str, Enum):
    CUSTOMER = "Customer"
    OWNER = "Restaurant Owner"

#Using basemodel this is what users will be filling out on a creation/registration form
class UserCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str = Field(..., min_length=8)
    role: UserRole

#Storing the user data internally
class User(BaseModel):
    id: int
    name: str
    password_hash: str
    email: str
    phone_number: str
    role: UserRole

