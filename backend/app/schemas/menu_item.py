from pydantic import BaseModel, Field, ConfigDict
from typing import List

class MenuItem(BaseModel):
    model_config = ConfigDict(validate_by_name=True)    #   To allow creating MenuItem using alias("price").

    id: int
    name: str
    description: str
    base_price: float = Field(alias="price", ge=0)
    percentage_discount: float = Field(default=0, ge=0, le=1)
    image_url: str
    add_ons: List[int]  #   add-ons' id
    is_available: bool
    restaurant_id: int 

    def get_price(self) -> float:
        return self.base_price * (1 - self.percentage_discount)