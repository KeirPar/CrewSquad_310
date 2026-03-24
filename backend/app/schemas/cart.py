from pydantic import BaseModel
from typing import List
from app.schemas.menu_item import MenuItem

class Cart(BaseModel):
    id: int
    menu_items: List[MenuItem]