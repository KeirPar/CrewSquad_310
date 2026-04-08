from fastapi.testclient import TestClient
from app.main import app
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.review import ReviewCreate
from fastapi import status
from app.schemas.user import UserRole
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData
from app.repositories.review_repo import review_db

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
    A user can create a new review for a restaurant with the following conditions:

    - is a customer or admin (cannot rate restaurant using restaurant or delivery driver account).
    - have ordered in the restaurant before.
    - can only create one review per user for a restaurant.
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

    #   Clear review_db
    review_db.clear_all()

    #   Add review
    response = client.post("/restaurants/" + str(restaurant_id) + "/reviews", json=ReviewCreate(content = "", rating = 10).model_dump())
    assert response.status_code == status.HTTP_200_OK

    #   Check the rating is applied
    rating_response = client.get("/restaurants/" + str(restaurant_id) + "/rating")
    assert rating_response.json() == 10

    #   update review rating
    new_rating = ReviewCreate(content = "Hello", rating = 5)
    response = client.post("/restaurants/" + str(restaurant_id) + "/reviews", json=new_rating.model_dump())
    assert response.status_code == status.HTTP_200_OK

    #   Check the average rating is updated.
    rating_response = client.get("/restaurants/" + str(restaurant_id) + "/rating")
    assert rating_response.json() == 5
    
    #   Check the review is updated.
    reviews_response = client.get("/restaurants/" + str(restaurant_id) + "/reviews")
    assert reviews_response.json()[0]["content"] == new_rating.content
    assert reviews_response.json()[0]["rating"] == new_rating.rating