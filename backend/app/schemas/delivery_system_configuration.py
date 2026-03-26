from pydantic import BaseModel

class DeliverySystemConfiguration(BaseModel):
    delivery_fee_multiplier: float = 1