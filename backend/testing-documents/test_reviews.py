from fastapi.testclient import TestClient
from app.main import app
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.review import ReviewCreate
from fastapi import status
from app.schemas.user import UserRole
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData

client = TestClient(app)
user_test_helper = UserTestHelper(client=client)

def test_add_review_as_restaurant_owner():
    """
    You cannot create review for restaurant as a restaurant owner, so this should throw 403 forbidden
    """

    #   Login
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.role = UserRole.OWNER
    user_test_helper.register_and_login_user(user=user_create)
    user_test_helper.login(user_create.email, user_create.password)

    #   Get all restaurants ids
    response = client.get("/search/restaurants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"] 
    restaurant_ids = [restaurant["id"] for restaurant in data]

    #   Add review
    response = client.post("/restaurants/" + str(restaurant_ids[0]) + "/reviews", json=ReviewCreate(content = "", rating = 5).model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_add_review_as_invalid_customer():
    """
    You cannot create review for restaurant if you have not order at the restaurant before, so this should throw 403 forbidden
    """
    #   Login
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.email = "Imacustomer@example.com"
    user_create.role = UserRole.CUSTOMER

    #   Get all restaurants ids
    response = client.get("/search/restaurants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"] 
    restaurant_ids = [restaurant["id"] for restaurant in data]

    #   Add review
    response = client.post("/restaurants/" + str(restaurant_ids[0]) + "/reviews", json=ReviewCreate(content = "", rating = 10).model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_add_review_as_valid_customer():
    """
    You cannot create review for restaurant if you have not order at the restaurant before, so this should throw 403 forbidden
    """
    #   Login
    user_test_helper = UserTestHelper(client=client)
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.email = "Imacustomer@example.com"
    user_create.role = UserRole.CUSTOMER

    user_test_helper.register_and_login_user(user=user_create)
    user_test_helper.login(user_create.email, user_create.password)

    #   Get first restaurants id
    response = client.get("/search/restaurants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"] 
    restaurant_ids = [restaurant["id"] for restaurant in data]
    restaurant_id = restaurant_ids[0]


    testing_data = TestingData(cart_restaurant_id=restaurant_id)
    #   Place order
    order_create = OrderCreate(
        user_id=user_test_helper.get_current_user().id,
        cart=testing_data.cart
    ).model_dump()

    response = client.post("/orders", json=order_create)

    #   Add review
    response = client.post("/restaurants/" + str(restaurant_id) + "/reviews", json=ReviewCreate(content = "", rating = 10).model_dump())
    assert response.status_code == status.HTTP_200_OK