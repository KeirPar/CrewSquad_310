from datetime import datetime, timezone, timedelta
from typing import Optional

from app.schemas.scheduled_order import ScheduledOrder, ScheduledOrderCreate
from app.schemas.order import OrderStatus
from app.repositories.scheduled_repo import scheduled_order_db
from app.repositories.user_repository import user_db
from app.repositories.restaurant_repo import RestaurantRepository
from app.services.order_service import create_order, validate_cart
from app.repositories.order_repo import order_db


PREPARATION_TIME_MINUTES = 20       # fixed kitchen preparation time
AVERAGE_SPEED_KMH = 30             # average city delivery speed in km/h
MAX_SCHEDULE_HOURS_AHEAD = 24      # orders cannot be scheduled more than 24h ahead

restaurant_repo = RestaurantRepository()


def estimate_delivery_minutes(user_coordinate, restaurant_id: int) -> float:
    """
    Estimates total delivery time in minutes.

    Calculation:
        - Preparation time: fixed 20 minutes
        - Travel time: distance (km) / average speed (30 km/h) * 60

    Args:
        user_coordinate: The customer's Coordinate object.
        restaurant_id (int): The ID of the restaurant.

    Returns:
        float: Total estimated delivery time in minutes.

    Raises:
        ValueError: If the restaurant is not found.
    """
    restaurant = restaurant_repo.find_by_id(restaurant_id)
    if restaurant is None:
        raise ValueError(f"Restaurant {restaurant_id} not found.")

    distance_km = user_coordinate.get_kilometer_distance_to(restaurant.coordinate)
    travel_minutes = (distance_km / AVERAGE_SPEED_KMH) * 60
    return PREPARATION_TIME_MINUTES + travel_minutes


def create_scheduled_order(scheduled_order_create: ScheduledOrderCreate, user_id: int) -> ScheduledOrder:
    """
    Creates and stores a scheduled order after full validation.

    Business Rules:
        — Cart must have at least 1 item all from the same restaurant.
        — scheduled_time must be in the future and within 24 hours from now.
        — scheduled_time must allow enough time for preparation and delivery.
              The system estimates delivery time using distance and rejects requests
              where the scheduled_time is earlier than the estimated delivery time.

    Args:
        scheduled_order_create (ScheduledOrderCreate): Cart and scheduled_time.
        user_id (int): The authenticated user's ID (from router).

    Returns:
        ScheduledOrder: The stored scheduled order with estimated delivery info.

    Raises:
        ValueError: If any business rule is violated.
    """
    now = datetime.now(timezone.utc)
    scheduled_time = scheduled_order_create.scheduled_time

    # Make timezone-aware if naive
    if scheduled_time.tzinfo is None:
        scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)


    if scheduled_time <= now:
        raise ValueError("Scheduled time must be in the future.")


    if scheduled_time > now + timedelta(hours=MAX_SCHEDULE_HOURS_AHEAD):
        raise ValueError(
            f"Scheduled time must be within {MAX_SCHEDULE_HOURS_AHEAD} hours from now."
        )

    cart = scheduled_order_create.cart
    if not cart.menu_items:
        raise ValueError("No items in cart.")
    validate_cart(cart)

    # Validate user exists
    user = user_db.find_by_user_id(user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found.")

    # FR3 — Validate scheduled_time allows enough time for delivery
    restaurant_id = cart.menu_items[0].restaurant_id
    estimated_minutes = estimate_delivery_minutes(user.coordinate, restaurant_id)
    estimated_delivery_time = now + timedelta(minutes=estimated_minutes)

    if scheduled_time < estimated_delivery_time:
        raise ValueError(
            f"Scheduled time does not allow enough time for delivery. "
            f"Estimated delivery takes {round(estimated_minutes)} minutes. "
            f"Please schedule for at least {estimated_delivery_time.strftime('%Y-%m-%dT%H:%M UTC')}."
        )

    # Create the underlying order with SCHEDULED status
    order_id = order_db.next_id()
    order = create_order(order_id=order_id, user_id=user_id, cart=cart)
    order.status = OrderStatus.SCHEDULED
    order_db.save(order)

    # Build and persist the scheduled order
    scheduled_order = ScheduledOrder(
        id=scheduled_order_db.next_id(),
        user_id=user_id,
        order=order,
        scheduled_time=scheduled_time,
        estimated_delivery_time=estimated_delivery_time,
        estimated_delivery_minutes=round(estimated_minutes, 2),
        created_at=now,
        is_cancelled=False,
        cancellation_reason=""
    )

    return scheduled_order_db.save(scheduled_order)


def cancel_scheduled_order(scheduled_order_id: int, user_id: int, reason: str = "") -> ScheduledOrder:
    """
    Cancels a scheduled order (FR4).

    Business Rules:
        - The scheduled order must exist.
        - Only the user who placed the order can cancel it.
        - The order must not already be cancelled.

    Args:
        scheduled_order_id (int): The ID of the scheduled order.
        user_id (int): The authenticated user's ID.
        reason (str): Optional reason for cancellation.

    Returns:
        ScheduledOrder: The updated scheduled order with is_cancelled=True.

    Raises:
        ValueError: If not found, not authorized, or already cancelled.
    """
    scheduled_order = scheduled_order_db.find_by_id(scheduled_order_id)

    if scheduled_order is None:
        raise ValueError(f"Scheduled order {scheduled_order_id} not found.")

    if scheduled_order.user_id != user_id:
        raise ValueError("You are not authorized to cancel this scheduled order.")

    if scheduled_order.is_cancelled:
        raise ValueError("This scheduled order has already been cancelled.")

    scheduled_order.is_cancelled = True
    scheduled_order.cancellation_reason = reason
    scheduled_order.order.status = OrderStatus.CANCELLED

    return scheduled_order


def get_my_scheduled_orders(user_id: int) -> list[ScheduledOrder]:
    """
    Returns all scheduled orders for the authenticated user (FR5).

    Args:
        user_id (int): The authenticated user's ID.

    Returns:
        list[ScheduledOrder]: All scheduled orders belonging to the user,
        sorted by scheduled_time ascending.
    """
    orders = scheduled_order_db.find_by_user_id(user_id)
    return sorted(orders, key=lambda so: so.scheduled_time)


def get_scheduled_order_by_id(scheduled_order_id: int) -> Optional[ScheduledOrder]:
    """
    Returns a single scheduled order by ID.

    Args:
        scheduled_order_id (int): The ID of the scheduled order.

    Returns:
        ScheduledOrder or None if not found.
    """
    return scheduled_order_db.find_by_id(scheduled_order_id)