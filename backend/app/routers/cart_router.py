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

from app.services.order_service import get_bill as calculate_bill

from app.schemas.menu_item import MenuItem
from app.schemas.cart import Cart
from app.services.menu_service import menu_service
from app.schemas.bill import Bill

#   TODO: get bill for cart.
@router.get("/bill")
def get_bill(user: User = Depends(AuthService.get_current_user)) -> Bill:
    menu_items = [menu_item for menu_item in menu_service.get_all_menu_items() if (menu_item.id in user.cart)]
    bill = calculate_bill(Cart(id=0, menu_items=menu_items), user=user, restaurant_id=menu_items[0].restaurant_id)
    return bill