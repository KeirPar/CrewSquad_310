from fastapi.testclient import TestClient
from app.main import app
from app.helpers.user_test_helper import UserTestHelper
from app.packages.geo.coordinate import Coordinate
from app.schemas.review import ReviewCreate
from fastapi import status

client = TestClient(app)
user_test_helper = UserTestHelper(client=client)

# def test_add_review_as_customer():
#     #   Login
#     user_create = user_test_helper.test_user_create.model_copy()
#     user_test_helper.register_and_login_user(user=user_create)
#     user_test_helper.login(user_create.email, user_create.password)

#     #   Get all restaurants ids
#     response = client.get("/search/restaurants")
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()["data"] 
#     restaurant_ids = [restaurant["id"] for restaurant in data]

#     #   Add ratings
#     for id in restaurant_ids:
#         client.post("/restaurants/" + str(id) + "/reviews", json=ReviewCreate(content = "", rating = 3 * id % 10).model_dump())

#     #   Check resturants ratings is sorted
#     rating_sorted_response = client.get("/search/restaurants?sort_by=rating_desc")
#     sorted_restaurants = rating_sorted_response.json()["data"]
#     restaurant_ratings = [client.get("restaurants/" + str(restaurant["id"]) + "/rating").json() for restaurant in sorted_restaurants]
#     assert restaurant_ratings == sorted(restaurant_ratings, reverse=True)