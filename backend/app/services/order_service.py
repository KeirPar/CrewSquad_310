from datetime import datetime, timezone 
from app.schemas.cart import Cart
from app.schemas.order import Order

def create_order(order_id: int, cart: Cart) -> Order:
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
    return Order(
        id=order_id,
        created_at=datetime.now(timezone.utc), #had to change this because .utcnow() was depreciated
        status="PENDING",
        restaurant_id=cart.menu_items[0].restaurant_id,
        items=cart.menu_items,
        total_amount=calculate_total(cart)
    )

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

def calculate_total(cart: Cart) -> float:
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
        total_price += item.price
    return total_price



"I just want to write a comment explaining fully how the status changing works to avoid any confusion,"
"so basically, once an order is created, it starts with the status PENDING. "
"From there, it can either be changed to PREPARING or CANCELLED. If it is changed to PREPARING, "
"then it can either be changed to DELIVERED or CANCELLED. Once an order is DELIVERED or CANCELLED, "
"it is locked and cannot be changed anymore. So you cant change a DELIVERED order to CANCELLED or anything like that. "
"This is just an example of how we can implement the status changing, we can change the valid transitions later if we want."


def update_order_status(order: Order, new_status: str) -> Order: #added for fr3
  
    new_status = new_status.upper() #Just make everything capital to avoid case sensitivity issues

    if order.status in ["DELIVERED", "CANCELLED"]: #check if order is already delivered or cancelled, if so, we cant update the status anymore
        raise ValueError(f"Order is locked and cannot be updated. Cant change the status from {order.status}") #return error
    
    valid_transitions = { #we have to make some valid status transitions. So orders can only go from PENDING to PREPARING or CANCELLED, and from PREPARING to DELIVERED or CANCELLED. This is just an example, we can change it later if we want
        "PENDING": ["PREPARING", "CANCELLED"],
        "PREPARING": ["DELIVERED", "CANCELLED"],
    }

    alowed_next_states = valid_transitions.get(order.status, []) #get the allowed next states for the current status of the order
    if new_status not in alowed_next_states: #if the new status is not in the allowed next states, return an error. So like if we try to change the status from PENDING to DELIVERED, it will return an error because that is not a valid transition
        raise ValueError(f"Invalid status transition from {order.status} to {new_status}. Allowed transitions: {alowed_next_states}")

    order.status = new_status #otherwise, all good. Change the status and return the order
    return order