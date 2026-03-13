from pydantic import BaseModel

class Delivery(BaseModel):
    id: int
    pickup_address: str
    dropoff_address: str
    dropoff_instructions: str
    status: str