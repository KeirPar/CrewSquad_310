from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.restaurant import Restaurant, restaurantCreate, RestaurantUpdate
from app.schemas.user import User
from app.dependencies import verify_restaurant_owner
from app.repositories.restaurant_repo import RestaurantRepository

#Initialize router with a prefix so all routes start with /restaurants
router = APIRouter(prefix="/restaurants", tags=["Restaurant Management"])
repo = RestaurantRepository()

@router.post("/register", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def register_restaurant(restaurant_in: restaurantCreate, owner: User = Depends(verify_restaurant_owner)):
    """Registers a new restaurant and links it to the logged in owner"""
    restaurants = repo.load_all()
    
    #Creating new restaurant 
    new_restaurant = {
        "id": len(restaurants) + 1,
        "owner_id": owner.id, # Crucial: Link the business to the owner
        "name": restaurant_in.name,
        "address": restaurant_in.address,
        "cuisine_type": restaurant_in.cuisine_type,
        "phone_number": restaurant_in.phone_number,
        "price_tier": restaurant_in.price_tier,
        "rating": 0.0,
        "is_open": True
    }
    
    #Add new one to list and save/return it
    restaurants.append(new_restaurant)
    repo.save_all(restaurants)
    return new_restaurant

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

    #Only update fields that were actually provided
    update_dict = update_data.model_dump(exclude_unset=True)
    
    #Loop and do again
    for key, value in update_dict.items():
        target[key] = value

    repo.save_all(restaurants)
    return target