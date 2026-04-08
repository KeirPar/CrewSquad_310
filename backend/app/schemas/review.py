from pydantic import BaseModel, Field

class Review(BaseModel):
    id: int
    content: str
    rating: float = Field(ge=0, le=10)
    user_id: int
    restaurant_id: int

class ReviewCreate(BaseModel):
    content: str
    rating: float = Field(ge=0, le=10)