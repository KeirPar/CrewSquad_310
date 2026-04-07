import queue
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.services.notification_service import create_order_notification, create_status_change_notifications
from app.services import order_service
from app.services.auth_service import AuthService
from app.schemas.cart import Cart
from app.services.order_service import create_order, get_pending_queue
from app.schemas.order import Order, OrderStatus
from app.schemas.customer import Customer
from app.schemas.restaurant_manager import RestaurantManager
from app.services.order_service import update_order_status, create_order
from app.schemas.user import User, UserRole
from app.services.payment_service import create_payment_attempt, simulate_payment
from app.schemas.order import OrderCreate
from app.repositories.order_repo import order_db
from app.repositories.payment_repo import payment_db
from app.services.auth_service import AuthService
from fastapi import status

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_current_user() -> User: #make fake user
    # same as the fake user from the test file
    return Customer( #change this to a restaurant manager if you want to test that instead
        id=1,
        name="Keir P",
        password_hash="hashthingy", 
        email="fake@gmail.com",
        phone_number="604-677-6767",
        role=UserRole.CUSTOMER,     
        default_address="123 Fake St", 
    )

def get_current_manager() -> RestaurantManager: #make fake manager
    return RestaurantManager(
        id=2,
        name="Bob Manager",
        password_hash="hashthingy",
        email="manager@gmail.com",
        phone_number="604-777-7777",
        role=UserRole.OWNER,
        address="456 Manager St",
        restaurant_id=5,
    )

@router.get("/")
def get_orders(user: User = Depends(AuthService.get_current_user)) -> list[Order]:
    return order_db.find_all_by_user_id(user.id)

@router.post("/")
def place_order(orderCreate: OrderCreate):
    """
    Endpoint to place an order based on the given cart. 
    Validates the cart and creates an order along with a payment attempt.
    Rules:
        - Must contain at least 1 Item
        - All items must be from the same restaurant
    Args:
        - orderCreate (OrderCreate): User id and the Cart object containing the menu items to be ordered
    Returns:
        - PaymentAttempt: A PaymentAttempt object representing the payment for the order
    """
    try:
        order = create_order(order_id = order_db.next_id(), user_id=orderCreate.user_id, cart=orderCreate.cart)
        order_db.save(order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    payment = create_payment_attempt(order) 
    create_order_notification(order) 
    return {**order.model_dump(), "payment": payment}

@router.get("/queue")
def get_pending_orders(current_user: User = Depends(AuthService.get_current_user)):
    
    if current_user.role != UserRole.OWNER: #make sure user is a manager/owner
        raise HTTPException(status_code=403, detail="Only restaurant managers can access the pending orders queue.")
    
    rest_id = getattr(current_user, "restaurant_id", 1) #get restaurant id from user, defaulting to 1 cuz we dont have a db
    
    pending_queue = order_service.get_pending_queue(rest_id) #otherwise, search by restaurant id

    return {
        "message": "Kitchen queue retrieved successfully",
        "pending_orders": pending_queue
    }


@router.get("/{order_id}")
def get_order_status(order_id: int):
    order = order_db.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment = payment_db.find_by_order_id(order_id)
    return {"order": order, "payment": payment}


@router.patch("/{order_id}/status")
def change_order_status(
    order_id: int,
    order: Order, 
    new_status: OrderStatus, 
    current_user: User = Depends(get_current_manager) #fake user until we have feat1 setup
):
    try:
        updated_order = update_order_status(
            order=order, 
            new_status=new_status, 
            current_user=current_user
        )
        create_status_change_notifications(updated_order, new_status, current_user) 
        return {"message": "Order status updated successfully", "data": updated_order}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))