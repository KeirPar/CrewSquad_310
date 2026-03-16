from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import verify_restaurant_owner
from app.schemas.menu import MenuItem, MenuItemCreate
from app.schemas.user import User
from app.repositories.restaurant_repo import RestaurantRepository

router = APIRouter(prefix="/menu", tags=["Menu Management"])
repo = RestaurantRepository()

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