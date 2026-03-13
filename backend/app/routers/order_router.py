from fastapi import APIRouter, HTTPException
from app.schemas.cart import Cart
from app.services.order_service import create_order

router = APIRouter()

@router.post("/orders")
def place_order(cart: Cart):
    """
    Endpoint to place an order based on the given cart.
    Rules:
        - Must contain at least 1 Item
        - All items must be from the same restaurant
    Args:
        - cart (Cart): The Cart object containing the menu items to be ordered
    Returns:
        - Order: An Order object containing the order details
    """
    try:
        return create_order(order_id=1, cart=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))