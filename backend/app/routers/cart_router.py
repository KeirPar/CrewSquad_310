from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User
from app.services.auth_service import AuthService
from app.repositories.user_repository import user_db

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])

@router.get("")
def get_cart(user: User = Depends(AuthService.get_current_user)):
    """Accesses shopping cart"""
    return {"cart_items": user.cart}

@router.post("/add/{item_id}")
def add_to_cart(item_id: int, user: User = Depends(AuthService.get_current_user)):
    """Allows user to add items to cart."""
    user.cart.append(item_id)
    return {"message": "Item added to cart", "current_cart": user.cart}