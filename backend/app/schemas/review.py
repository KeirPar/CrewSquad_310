from pydantic import BaseModel

class Review(BaseModel):
    content: str
    rating: float
    user_id: int