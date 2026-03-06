from pydantic import BaseModel

class Resturant(BaseModel):
    id: int
    name: str
    address: str
    cuisine_type: str
    rating: float
    is_open: bool