from fastapi.testclient import TestClient
from app.main import create_app
from app.helpers.user_test_helper import UserTestHelper
from app.packages.geo.coordinate import Coordinate
from app.schemas.review import ReviewCreate
from fastapi import status
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData
from app.schemas.user import UserRole

client = TestClient(create_app())
user_test_helper = UserTestHelper(client=client)

def test_sort_by_rating_desc():
    #   Login
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.email = "ABC@example.com"
    user_create.role = UserRole.CUSTOMER
    user_test_helper.register_and_login_user(user=user_create)
    user_test_helper.login(user_create.email, user_create.password)

    #   Get all restaurants ids
    response = client.get("/search/restaurants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"] 
    restaurant_ids = [restaurant["id"] for restaurant in data]

    #   Add ratings
    for id in restaurant_ids:
        testing_data = TestingData(cart_restaurant_id=id)
        order_create = OrderCreate(
            user_id=user_test_helper.get_current_user().id,
            cart=testing_data.cart
        ).model_dump()
        response = client.post("/orders", json=order_create)

        add_review_response = client.post("/restaurants/" + str(id) + "/reviews", json=ReviewCreate(content = "", rating = 3 * id % 10).model_dump())
        print(add_review_response.text)
        assert add_review_response.status_code == status.HTTP_200_OK

    #   Check resturants ratings is sorted
    rating_sorted_response = client.get("/search/restaurants?sort_by=rating_desc")
    sorted_restaurants = rating_sorted_response.json()["data"]
    restaurant_ratings = [client.get("restaurants/" + str(restaurant["id"]) + "/rating").json() for restaurant in sorted_restaurants]
    assert restaurant_ratings == sorted(restaurant_ratings, reverse=True)

def test_sort_by_price_asc():
    response = client.get("/search/restaurants?sort_by=price_asc")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]

    if len(data) > 1: #here we check if the price is sorted low to high, but again only if we have more than 1 restaurant in the results
        assert data[0]["price_tier"] <= data[1]["price_tier"]

def test_sort_by_distance_asc():
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(latitude=49.94290035633633, longitude=-119.39555529342739)   
    user_test_helper.register_and_login_user(user=user_create)
    
    response = client.get("/search/restaurants?sort_by=distance_asc", headers={"Authorization": f"Bearer {user_test_helper.login_token}"})
    assert response.status_code == status.HTTP_200_OK
    restaurants = response.json()["data"]
    
    if len(restaurants) > 1:
            sorted_restaurants = sorted(
                restaurants,
                key=lambda r: (
                    not r.get("is_open", True), 
                    float(Coordinate(**r.get("coordinate")).get_kilometer_distance_to(user_create.coordinate))
                )
            )

    print("\nAPI Order:", [r["name"] for r in restaurants])
    print("Test Order:", [r["name"] for r in sorted_restaurants])

    assert restaurants == sorted_restaurants
