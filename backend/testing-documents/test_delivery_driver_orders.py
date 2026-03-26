import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import create_app
from app.helpers.user_test_helper import UserTestHelper
from app.helpers.testing_data import TestingData
from app.packages.geo.coordinate import Coordinate
from app.schemas.order import Order
from app.schemas.user import UserRole
from app.repositories.order_repo import order_db
from app.repositories.helpers.repository_manager import RepositoryManager

client = TestClient(create_app())
user_test_helper = UserTestHelper(client=client)
testing_data = TestingData()

user_count: int = 0
DELIVERY_NOTE = "The door password is 675267"

#   Clear database before testing each function, to ensure data is independent between functions. (Results won't affect each other)
@pytest.fixture(scope="function", autouse=True)
def clean_up():
    RepositoryManager.reset_all_repositories()

def order_at_coordinate(coordinate: Coordinate):
    global user_count

    user_create = user_test_helper.test_user_create.model_copy()
    user_create.email = "91241204" + str(user_count) + "@example.com"
    user_create.coordinate = coordinate
    user_create.delivery_note = DELIVERY_NOTE
    user = user_test_helper.register_and_login_user(user=user_create)

    create_order_response = client.post("/orders", json={ 
        "user_id": user.id, 
        "cart": testing_data.cart.model_dump() 
    })

    user_count += 1

def test_customer_get_orders():
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.email = "imacustomer" + str(user_count) + "@example.com"
    user_create.role = UserRole.CUSTOMER
    user_test_helper.register_and_login_user(user=user_create)

    response = client.get("/driver/orders?max_km=100")
    assert response.status_code == status.HTTP_403_FORBIDDEN  #   It failed because only driver can get other orders


def test_get_nearby_orders():
    #   Create users
    order_at_coordinate(Coordinate(0, 0.01))
    order_at_coordinate(Coordinate(0.01, 0.02))
    order_at_coordinate(Coordinate(45, 90))

    #   Create delivery driver
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(0, 0)
    user_create.role = UserRole.DELIVERY_DRIVER
    delivery_driver = user_test_helper.register_and_login_user(user=user_create)

    response = client.get("/driver/orders?max_km=100")
    orders: list[dict] = response.json()
    for raw_order in orders:
        order = Order(**raw_order)
        order.delivery_note = DELIVERY_NOTE
    assert len(orders) == 2 #   Only the first two order that is close to the driver coordinate will be retrieved.

def test_get_impossible_distance_orders():
    #   Create users
    order_at_coordinate(Coordinate(0, 0.01))
    order_at_coordinate(Coordinate(0.01, 0.02))
    order_at_coordinate(Coordinate(45, 90))

    #   Create delivery driver
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(0, 0)
    user_create.role = UserRole.DELIVERY_DRIVER
    delivery_driver = user_test_helper.register_and_login_user(user=user_create)

    response = client.get("/driver/orders?max_km=0")
    orders: list[dict] = response.json()
    assert len(orders) == 0

def test_get_long_distance_orders():
    #   Create users
    order_at_coordinate(Coordinate(0, 0.01))
    order_at_coordinate(Coordinate(0.01, 0.02))
    order_at_coordinate(Coordinate(45, 90))

    #   Create delivery driver
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(0, 0)
    user_create.role = UserRole.DELIVERY_DRIVER
    delivery_driver = user_test_helper.register_and_login_user(user=user_create)

    response = client.get("/driver/orders?max_km=99999999999.676767")
    orders: list[dict] = response.json()
    assert len(orders) == 3

def test_distance_sort():
    #   Create users, where coordinates are unordered
    order_at_coordinate(Coordinate(0, 0.01))
    order_at_coordinate(Coordinate(45, 90))
    order_at_coordinate(Coordinate(0.01, 0.02))


    #   Create delivery driver
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(0, 0)
    user_create.role = UserRole.DELIVERY_DRIVER
    delivery_driver = user_test_helper.register_and_login_user(user=user_create)

    response = client.get("/driver/orders?max_km=99999999999.676767")
    orders: list[dict] = response.json()
    
    sorted_orders = sorted(
        orders,
        key=lambda order: float(Coordinate(**order.get("coordinate")).get_kilometer_distance_to(user_create.coordinate)),
        reverse=False
    )
    assert orders == sorted_orders