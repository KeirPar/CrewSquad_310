from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    password_hash: str
    email: str
    phone_number: str