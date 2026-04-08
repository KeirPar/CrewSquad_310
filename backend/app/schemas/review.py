from pydantic import BaseModel

class Review(BaseModel):
    id: int
    content: str
    rating: float
    user_id: int
    restaurant_id: int

class ReviewCreate(BaseModel):
    content: str
    rating: float