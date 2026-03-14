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




def update_order_status(order: Order, new_status: str) -> Order: #added for fr3
  
    new_status = new_status.upper() #Just make everything capital to avoid case sensitivity issues

    if order.status in ["DELIVERED", "CANCELLED"]: #check if order is already delivered or cancelled, if so, we cant update the status anymore
        raise ValueError(f"Order is locked and cannot be updated. Cant change the status from {order.status}") #return error
  
    order.status = new_status #otherwise, all good. Change the status and return the order
    return order