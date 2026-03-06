from pydantic import BaseModel
from typing import List

class MenuItem(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    add_ons: List[int]  #   add-ons' id
    is_available: bool