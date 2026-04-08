from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, User
from app.services.auth_service import AuthService
from app.repositories.order_repo import OrderRepository


order_db = OrderRepository()

router = APIRouter(prefix="/user", tags = ["User"])

@router.post("/update")
def update_user(updated_user_data: UserCreate, user: User = Depends(AuthService.get_current_user)):
    user.name = updated_user_data.name
    user.email = updated_user_data.email
    user.phone_number = updated_user_data.phone_number
    user.password_hash = AuthService.hash_password(updated_user_data.password)
    user.role = updated_user_data.role
    user.address = updated_user_data.address
    user.delivery_note = updated_user_data.delivery_note

    return {"message": "User updated successfully", "user" : user}

@router.post("/favourites/items/{item_id}", status_code=status.HTTP_200_OK)
def add_favourite_item(item_id: int, user: User = Depends(AuthService.get_current_user)):
    """Adds a menu item to the user's favourites list."""
    if item_id in user.favourite_items:
        raise HTTPException(status_code=400, detail="Item is already in favourites list.")
    
    user.favourite_items.append(item_id)
    return {"message": "Item added to favourites list", "favourite_items": user.favourite_items}

@router.delete("/favourites/items/{item_id}", status_code=status.HTTP_200_OK)
def delete_favourite_item(item_id: int, user: User = Depends(AuthService.get_current_user)):
    """Delete a menu item from the user's favourites list."""
    if item_id not in user.favourite_items:
        raise HTTPException(status_code=404, detail="Item not found in your favourites list.")
    
    user.favourite_items.remove(item_id)
    return {"message": "Item removed from favourites list", "favourite_items": user.favourite_items}

@router.post("/favourites/restaurants/{restaurant_id}", status_code=status.HTTP_200_OK)
def add_favourite_restaurant(restaurant_id: int, user: User = Depends(AuthService.get_current_user)):
    """Adds a restaurant to the user's favourites list."""
    if restaurant_id in user.favourite_restaurants:
        raise HTTPException(status_code=400, detail="Restaurant is already in your favourites list.")
    
    user.favourite_restaurants.append(restaurant_id)
    return {"message": "Restaurant added to favourites list", "favourite_restaurants": user.favourite_restaurants}

@router.delete("/favourites/restaurants/{restaurant_id}", status_code=status.HTTP_200_OK)
def delete_favourite_restaurant(restaurant_id: int, user: User = Depends(AuthService.get_current_user)):
    """Deletes a restaurant from the user's favourites list."""
    if restaurant_id not in user.favourite_restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found in your favourites list.")
    
    user.favourite_restaurants.remove(restaurant_id)
    return {"message": "Restaurant removed from favourites lists", "favourite_restaurants": user.favourite_restaurants}

@router.get("/recently-ordered", status_code=status.HTTP_200_OK)
def get_recently_ordered_items(user: User = Depends(AuthService.get_current_user)):
    """Returns a list of the user's most recently ordered unique menu items."""
    recent_items = []
    seen_item_ids = set()

    #This goes through the user's order history backwards to get most recent orders
    for order_id in reversed(user.order_history):
        order = order_db.find_by_id(order_id)
        
        if order:
            for item in order.items:
                if item.id not in seen_item_ids:
                    seen_item_ids.add(item.id)
                    recent_items.append(item)
                    
                    #Just cap the list at 10 items, this can be whatever item we want
                    if len(recent_items) >= 10:
                        return {"recent_items": recent_items}

    return {"recent_items": recent_items}