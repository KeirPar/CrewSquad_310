import queue
from fastapi import APIRouter, Depends, HTTPException
from app.services import order_service
from app.services.auth_service import AuthService
from app.schemas.cart import Cart
from app.services.order_service import create_order, get_pending_queue
from app.schemas.order import Order, OrderStatus
from app.schemas.customer import Customer
from app.schemas.restaurant_manager import RestaurantManager
from app.services.order_service import update_order_status, create_order
from app.schemas.user import User, UserRole
from app.services.payment_service import create_payment_attempt

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
    Validates the cart and creates an order along with a payment attempt.
    Rules:
        - Must contain at least 1 Item
        - All items must be from the same restaurant
    Args:
        - cart (Cart): The Cart object containing the menu items to be ordered
    Returns:
        - PaymentAttempt: A PaymentAttempt object representing the payment for the order
    """
    try:
        order = create_order(order_id=1, cart=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    payment = create_payment_attempt(order)  # new
    return {**order.model_dump(), "payment": payment}  

@router.patch("/orders/{order_id}/status")
def change_order_status(
    order_id: int,
    order: Order, 
    new_status: OrderStatus, 
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

@router.get("/orders/queue")
def get_pending_orders(current_user: User = Depends(AuthService.get_current_user)):
    
    if current_user.role != UserRole.OWNER: #make sure user is a manager/owner
        raise HTTPException(status_code=403, detail="Only restaurant managers can access the pending orders queue.")
    
    rest_id = getattr(current_user, "restaurant_id", 1) #get restaurant id from user, defaulting to 1 cuz we dont have a db
    
    pending_queue = order_service.get_pending_queue(rest_id) #otherwise, search by restaurant id

    return {
        "message": "Kitchen queue retrieved successfully",
        "pending_orders": pending_queue
    }
