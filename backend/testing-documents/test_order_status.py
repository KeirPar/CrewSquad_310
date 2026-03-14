import pytest
from datetime import datetime, timezone
from app.schemas.order import Order
from app.services.order_service import update_order_status

#Here we dont need to import fastAPI test client because we are testing the service function directly
#we talk about this in slide 16 of the testing lab, its a unit test not an intergration test.

def create_dummy_order(status: str) -> Order: #creating dummy order
    return Order(id=1, created_at=datetime.now(timezone.utc), status=status, restaurant_id=1, items=[], total_amount=67.67) #.utcnow() was depreciated

def test_update_status_locked_delivered():
    order = create_dummy_order(status="DELIVERED") #make the status delivered (locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, "CANCELLED") #try to change the status to cancelled, should raise error because the order is locked
    assert "Order is locked" in str(excinfo.value)


def test_forward_success():
    order = create_dummy_order(status="PENDING") #make the status pending (not locked)
    updated_order = update_order_status(order, "PREPARING") #try to change the status to preparing, should work because the order is not locked
    assert updated_order.status == "PREPARING" #check that the status was updated correctly


def test_invalid_transition():
    order = create_dummy_order(status="PENDING") #make the status pending (not locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, "DELIVERED") #try to change the status to delivered, should raise error because you cant do this
    assert "Invalid status transition" in str(excinfo.value)