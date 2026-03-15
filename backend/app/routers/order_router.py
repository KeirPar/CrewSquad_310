from fastapi import APIRouter, Depends, HTTPException
from app.schemas.cart import Cart
from app.services.order_service import create_order
from app.schemas.order import Order
from app.schemas.customer import Customer
from app.schemas.restaurant_manager import RestaurantManager
from app.services.order_service import update_order_status, create_order
from app.schemas.user import User

router = APIRouter()

def get_current_user() -> User: # because we dont have feat1 setup
    # same as the fake user from the test file
    return Customer( #change this to a restaurant manager if you want to test that instead
        id=1,
        name="Keir P",
        password_hash="hashthingy", 
        email="fake@gmail.com",
        phone_number="604-677-6767",
        default_address="123 Fake St", #gonna have to change if this is a restaurant manager, like for testing
    )

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

@router.patch("/orders/{order_id}/status")
def change_order_status(
    order_id: int,
    order: Order, 
    new_status: str, 
    current_user: User = Depends(get_current_user) #fake user until we have feat1 setup
):
    try:
        updated_order = update_order_status(
            order=order, 
            new_status=new_status, 
            current_user=current_user
        )
        return {"message": "Order status updated successfully", "data": updated_order}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))