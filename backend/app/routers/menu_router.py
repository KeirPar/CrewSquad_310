from fastapi import APIRouter, Depends
from app.dependencies import verify_restaurant_owner

router = APIRouter(prefix="/menu", tags=["Menu Management"])

@router.post("/add", dependencies=[Depends(verify_restaurant_owner)])
def add_menu_item():
    """ Only Restaurant Owners can see success message, customers will get 403 forbidden."""

    return{"message": "Menu item added successfully!"}