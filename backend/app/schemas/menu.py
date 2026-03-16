from pydantic import BaseModel
from typing import List, Optional

#creating base menu models for future by using base model found in menu_item.py
class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    is_available: bool = True
    add_ons: List[int] = [] 

class MenuItemCreate(MenuItemBase):
    """Used for POST requests and excludes IDs"""
    pass

class MenuItem(MenuItemBase):
    """The full model stored in JSON"""
    id: int
    restaurant_id: int