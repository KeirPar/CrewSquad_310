from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import verify_restaurant_owner
from app.schemas.menu import MenuItem, MenuItemCreate, MenuItemUpdate
from app.schemas.user import User
from app.repositories.restaurant_repo import RestaurantRepository
from typing import List

router = APIRouter(prefix="/menu", tags=["Menu Management"])
repo = RestaurantRepository()

#Get function for menu
@router.get("/{restaurant_id}", response_model=List[MenuItem])
def get_restaurant_menu(restaurant_id: int):
    """Allows viewing of the full menu of a restaurant."""
    restaurants = repo.load_all()
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)
    
    #Exceptions if restaurant not found
    if not target:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    #Return the menu or an empty list
    return target.get("menu", [])

#add function for menu
@router.post("/{restaurant_id}/add", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def add_menu_item(
    restaurant_id: int, 
    item_in: MenuItemCreate, 
    owner: User = Depends(verify_restaurant_owner)
):
    """Allows an owner to add a dish to their specific restaurant menu."""
    restaurants = repo.load_all()
    
    #Find the restaurant
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    #Verify the id matches the restaurant's owner_id
    if target["owner_id"] != owner.id:
        raise HTTPException(
            status_code=403, 
            detail="You do not have permission to modify this restaurant's menu"
        )

    #Add to repository
    return repo.add_menu_item(restaurant_id, item_in.model_dump())

#Update function for menu
@router.patch("/{restaurant_id}/{item_id}", response_model=MenuItem)
def update_menu_item(
    restaurant_id: int, 
    item_id: int, 
    update_in: MenuItemUpdate, 
    owner: User = Depends(verify_restaurant_owner)
):
    """Allows an owner to update a menu item."""
    restaurants = repo.load_all()
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)


    #Exceptions on id != owner id or failure on update
    if not target or target["owner_id"] != owner.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this menu")

    updated_item = repo.update_menu_item(restaurant_id, item_id, update_in.model_dump(exclude_unset=True))
    
    if not updated_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return updated_item

#delete function for menu
@router.delete("/{restaurant_id}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int, 
    item_id: int, 
    owner: User = Depends(verify_restaurant_owner)
):
    """Allows an owner to delete a menu item."""
    restaurants = repo.load_all()
    target = next((r for r in restaurants if r["id"] == restaurant_id), None)

    #Exceptions on id != owner id or failure on deletion
    if not target or target["owner_id"] != owner.id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this menu")

    success = repo.delete_menu_item(restaurant_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return None
