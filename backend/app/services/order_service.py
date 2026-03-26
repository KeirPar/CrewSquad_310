from datetime import datetime, timezone

from fastapi import HTTPException 
from app.schemas.cart import Cart
from app.schemas.order import Order, OrderStatus
from app.schemas.user import User
from app.schemas.customer import Customer
from app.schemas.restaurant_manager import RestaurantManager
from app.schemas.bill import Bill
from app.services.auth_service import AuthService
from app.repositories.user_repository import user_db
from app.repositories.order_repo import order_db
from app.services.fees.tax_type import TaxType
from app.repositories.restaurant_repo import RestaurantRepository
from app.schemas.restaurant import Restaurant
from .fees.get_province_tax import get_province_tax
from .fees.get_delivery_fee import get_delivery_fee
from app.repositories.delivery_system_configuration_repo import delivery_system_configuration
from app.packages.geo.coordinate import Coordinate


def create_order(order_id: int, user_id: int, cart: Cart) -> Order:
    """
    checks if the cart is valid and creates an order with the given cart
    Rules:
        - Must contain at least 1 Item
        - All items must be from the same restaurant
    Args:
        - order_id (int): The unique ID for the order as an integer
        - cart (Cart): The Cart object containing the menu items to be ordered
    Returns:
        - Order: An Order object containing the order details
    """
    
    if not cart.menu_items:
        raise ValueError("No items in Cart")
    validate_cart(cart)

    user = user_db.find_by_user_id(user_id)
    user.order_history.append(order_id)

    if user is None:
        raise ValueError("Cart does not belongs to any user")
        
    restaurant_id=cart.menu_items[0].restaurant_id
    bill = get_bill(cart, user=user, restaurant_id=restaurant_id)
    order = Order(
        id=order_id,
        created_at=datetime.now(timezone.utc), #had to change this because .utcnow() was depreciated
        status=OrderStatus.PENDING,
        restaurant_id=restaurant_id,
        items=cart.menu_items,
        delivery_address=user.address,
        delivery_note=user.delivery_note,
        coordinate=user.coordinate,
        bill=bill
    )

    return order

def validate_cart(cart: Cart):
    """
    Validates the cart according to the following rules:
        - Must contain at least 1 Item
        - All items must be from the same restaurant
    Args:
        - cart (Cart): The Cart object containing the menu items to be ordered
    Returns:
        - None
    """

    first_restaurant = cart.menu_items[0].restaurant_id
    for item in cart.menu_items:
        if item.restaurant_id != first_restaurant:
            raise ValueError("Pick Items from one restaurant only")
        
def get_bill(cart: Cart, user: User, restaurant_id: int) -> Bill:
    province_tax = get_province_tax("BC")   #   TODO: Use `User.address.province` instead
    items_subtotal = calculate_items_subtotal(cart)
    tax_rates: list[(TaxType, float)] = province_tax.tax_rates

    taxes: list[(TaxType, float)] = [(tax_rate[0], tax_rate[1] * items_subtotal) for tax_rate in tax_rates] #   Convert a list of tax rates to tax by multiplying with item subtotal
    restuarant_repo = RestaurantRepository()
    restuarant: Restaurant = restuarant_repo.find_by_id(restaurant_id)
    distanceInKilometer: float = user.coordinate.get_kilometer_distance_to(restuarant.coordinate)

    delivery_fee = get_delivery_fee(distanceInKilometers=distanceInKilometer) * delivery_system_configuration.delivery_fee_multiplier

    return Bill(
        items_subtotal=items_subtotal,
        taxes=taxes,
        delivery_fee=delivery_fee
    )

def calculate_items_subtotal(cart: Cart) -> float:
    """
    Calculates the total amount for the given cart.
    Rules:
    - The total amount is the sum of the prices of all items in the cart
    Args:
        - cart (Cart): The Cart object containing the menu items to be ordered
    Returns:
        - float: The total amount for the order
    """
    
    total_price = 0
    for item in cart.menu_items:
        total_price += item.get_price()
    return total_price



"I just want to write a comment explaining fully how the status changing works to avoid any confusion,"
"so basically, once an order is created, it starts with the status PENDING. "
"From there, it can either be changed to PREPARING or CANCELLED. If it is changed to PREPARING, "
"then it can either be changed to DELIVERED or CANCELLED. Once an order is DELIVERED or CANCELLED, "
"it is locked and cannot be changed anymore. So you cant change a DELIVERED order to CANCELLED or anything like that. "

def update_order_status(order: Order, new_status: OrderStatus, current_user: User) -> Order: #added for fr3
  
    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]: #check if order is already delivered or cancelled, if so, we cant update the status anymore
        raise HTTPException(status_code=400, detail=f"Order is locked and cannot be updated. Cant change the status from {order.status}") #return error
    
    if isinstance(current_user, Customer):  # if current user is a customer, they can only cancel order if its pending
        if new_status != OrderStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Customers can only cancel orders. Invalid status update.")
        if order.status != OrderStatus.PENDING: 
            raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage. Only pending orders can be cancelled.")
    
    elif isinstance(current_user, RestaurantManager):  # but if its a manager then its chill
        pass
    else:
        raise HTTPException(status_code=403, detail="Unauthorized user class.")
        
    valid_transitions = { #we have to make some valid status transitions. So orders can only go from PENDING to PREPARING or CANCELLED, and from PREPARING to DELIVERED or CANCELLED. This is just an example, we can change it later if we want
        OrderStatus.PENDING: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
    }

    alowed_next_states = valid_transitions.get(order.status, []) #get the allowed next states for the current status of the order
    if new_status not in alowed_next_states: #if the new status is not in the allowed next states, return an error. So like if we try to change the status from PENDING to DELIVERED, it will return an error because that is not a valid transition
        raise HTTPException(status_code=400, detail=f"Invalid status transition from {order.status} to {new_status}. Allowed transitions: {alowed_next_states}")

    order.status = new_status #otherwise, all good. Change the status and return the order
    return order

def get_pending_queue(restaurant_id: int) -> list[Order]: #added for us3
    #returns a list of all pending orders for a restaurant, sorted by oldest first

    all_orders = [] #this would be like fetching all orders from the db, however we dont have any orders in a db

    pending_queue = [order for order in all_orders if order.restaurant_id == restaurant_id and order.status == OrderStatus.PENDING] 
    pending_queue.sort(key=lambda x: x.created_at) 
    return pending_queue

def get_orders_by_distance(from_coordinate: Coordinate, max_kilometer_distance: float) -> list[Order]:
    orders_in_distance = []

    for order in order_db._orders:
        order: Order = order
        if order.coordinate.get_kilometer_distance_to(from_coordinate) < max_kilometer_distance:
            orders_in_distance.append(order)

    
    orders_in_distance.sort(
        key=lambda order: float(order.coordinate.get_kilometer_distance_to(from_coordinate)) if order.coordinate is not None else 9999999999999,
        reverse=False
    )

    return orders_in_distance