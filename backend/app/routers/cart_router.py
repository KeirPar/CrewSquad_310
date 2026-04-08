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

@router.delete("/remove/{item_id}")
def remove_from_cart(item_id: int, user: User = Depends(AuthService.get_current_user)):
    """Allows user to remove an item from their cart."""
    if item_id in user.cart:
        user.cart.remove(item_id)
        return {"message": "Item removed from cart", "current_cart": user.cart}
    else:
        raise HTTPException(status_code=404, detail="No items in cart to remove.")

@router.delete("/clear")
def clear_cart(user: User = Depends(AuthService.get_current_user)):
    """Allows user to empty entire shopping cart."""
    user.cart.clear()  #This wipes the list
    return {"message": "Cart cleared successfully", "current_cart": user.cart}
    