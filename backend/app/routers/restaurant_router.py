from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.restaurant import Restaurant, restaurantCreate, RestaurantUpdate
from app.schemas.user import User
from app.dependencies import verify_restaurant_owner, verify_customer
from app.repositories.restaurant_repo import RestaurantRepository
from app.repositories.review_repo import review_db
from app.schemas.review import ReviewCreate, Review
from app.services.rating_service import get_average_rating
from app.repositories.order_repo import order_db
from typing import List 

#Initialize router with a prefix so all routes start with /restaurants
router = APIRouter(prefix="/restaurants", tags=["Restaurant Management"])
repo = RestaurantRepository()

@router.post("/register", response_model=Restaurant, status_code=status.HTTP_201_CREATED) #CHANGED THIS WHOLE FUNCTION TO UPDATED REPO ONE
def register_restaurant(restaurant_in: restaurantCreate, owner: User = Depends(verify_restaurant_owner)):
    """Registers a new restaurant using the Repository method."""
    #pass the owner_id manually to ensure the link is secure
    data = restaurant_in.model_dump()
    data["owner_id"] = owner.id
    
    return repo.create_restaurant(data)

@router.patch("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: int, 
    update_data: RestaurantUpdate, 
    owner: User = Depends(verify_restaurant_owner)
):
    """Allows owners to update specific fields of their restaurant"""
    restaurants = repo.load_all()
    
    #Find the restaurant and verify using id using if statements
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if target["owner_id"] != owner.id:
        raise HTTPException(status_code=403, detail="You do not own this restaurant")

    #update using new repo method calling the functions
    updated = repo.update_restaurant(restaurant_id, update_data.model_dump(exclude_unset=True))
    return updated

@router.get("/my-restaurant", response_model=List[Restaurant])
def get_my_restaurant(owner: User = Depends(verify_restaurant_owner)):
    """View all businesses registered using their id."""
    restaurants = repo.load_all()
    #Filter the list to only show shops belonging to the respective owner
    return [r for r in restaurants if r.get("owner_id") == owner.id] #cleaned this up some more

#delete function added using updated repo features
@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int, 
    owner: User = Depends(verify_restaurant_owner)
):
    """Deletes a restaurant and its entire menu (Cascading Delete)."""
    restaurants = repo.load_all()
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if target["owner_id"] != owner.id:
        raise HTTPException(status_code=403, detail="You do not own this restaurant")

    #This triggers the cascade I made in the restaurant repo
    repo.delete_restaurant(restaurant_id)
    return None

@router.post("/{restaurant_id}/reviews")
def review_restaurant(
    restaurant_id: int, 
    review_create: ReviewCreate,
    customer: User = Depends(verify_customer)
) -> Review:
    review = Review(
        id=0, 
        content=review_create.content, 
        rating=review_create.rating,
        user_id=customer.id,
        restaurant_id=restaurant_id
    )
    customer_orders_ids = customer.order_history
    has_customer_ordered_in_restaurant = restaurant_id in customer_orders_ids

    if not has_customer_ordered_in_restaurant:
        raise HTTPException(status_code=403, detail="You have not ordered in this restaurant")


    review_db.save(review)
    return review

@router.get("/{restaurant_id}/reviews", response_model=List[Review])
def get_retaurant_reviews(
    restaurant_id: int
):
    return [review for review in review_db.get_all_reviews() if review.restaurant_id == restaurant_id]

@router.get("/{restaurant_id}/rating")
def get_retaurant_rating(
    restaurant_id: int
) -> float:
    return get_average_rating(restaurant_id=restaurant_id)