import pytest
from datetime import datetime, timezone
from app.schemas.order import Order, OrderStatus
from app.services.order_service import update_order_status
from app.schemas.customer import Customer
from app.schemas.user import UserRole
from app.schemas.restaurant_manager import RestaurantManager

#Here we dont need to import fastAPI test client because we are testing the service function directly
#we talk about this in slide 16 of the testing lab, its a unit test not an intergration test.


fake_customer = Customer( #example customer
    id=1,
    name="Keir P",
    password_hash="hashthingy", 
    email="fake@gmail.com",
    phone_number="604-677-6767",
    default_address="123 Fake St",
    address="123 Fake St",
    role=UserRole.CUSTOMER
) 

fake_manager = RestaurantManager(
    id=2, 
    name="Bob", 
    password_hash="hash123", 
    email="bob@restaurant.com", 
    phone_number="250-555-6767", 
    address="123 Fake St",
    restaurant_id=1,
    role=UserRole.OWNER
)

def create_dummy_order(status: OrderStatus) -> Order: #creating dummy order
    return Order(id=1, created_at=datetime.now(timezone.utc), status=status, restaurant_id=1, items=[], total_amount=67.67) #.utcnow() was depreciated

def test_update_status_locked_delivered():
    order = create_dummy_order(status=OrderStatus.DELIVERED) #make the status delivered (locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, OrderStatus.CANCELLED, fake_customer) #try to change the status to cancelled, should raise error because the order is locked
    assert "Order is locked" in str(excinfo.value)


def test_forward_success():
    order = create_dummy_order(status=OrderStatus.PENDING) #make the status pending (not locked)
    updated_order = update_order_status(order, OrderStatus.PREPARING, fake_manager) #try to change the status to preparing, should work because the order is not locked
    assert updated_order.status == OrderStatus.PREPARING #check that the status was updated correctly


def test_invalid_transition():
    order = create_dummy_order(status=OrderStatus.PENDING) #make the status pending (not locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, OrderStatus.DELIVERED, fake_manager) #try to change the status to delivered, should raise error because you cant do this
    assert "Invalid status transition" in str(excinfo.value)

def test_customer_cancel_pending():
    order = create_dummy_order(status=OrderStatus.PENDING) #make the status pending (not locked)
    updated_order = update_order_status(order, OrderStatus.CANCELLED, fake_customer) 
    assert updated_order.status == OrderStatus.CANCELLED 
def test_customer_cancel_preparing():
    order = create_dummy_order(status=OrderStatus.PREPARING) #make the status preparing (not locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, OrderStatus.CANCELLED, fake_customer) #try to change the status to cancelled, should raise error because you can only cancel pending orders
    assert "Order cannot be cancelled at this stage" in str(excinfo.value)

def test_customer_cannot_accept_order():
    order = create_dummy_order(status=OrderStatus.PENDING) #make the status pending (not locked)
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, OrderStatus.PREPARING, fake_customer) #try to change the status to preparing, should raise error because customers can only cancel orders
    assert "Customers can only cancel orders" in str(excinfo.value)

def test_unauthorized_user():
    order = create_dummy_order(status=OrderStatus.PENDING) #make the status pending (not locked)
    class UnauthorizedUser:
        pass
    fake_user = UnauthorizedUser()
    with pytest.raises(ValueError) as excinfo:
        update_order_status(order, OrderStatus.PREPARING, fake_user) #try to change the status to preparing, should raise error because the user class is unauthorized
    assert "Unauthorized user class" in str(excinfo.value)

def test_manager_can_cancel_preparing():
    order = create_dummy_order(status=OrderStatus.PREPARING) #make the status preparing (not locked)
    updated_order = update_order_status(order, OrderStatus.CANCELLED, fake_manager) 
    assert updated_order.status == OrderStatus.CANCELLED #should work because restaurant managers can cancel orders at any stage