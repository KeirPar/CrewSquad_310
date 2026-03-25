from fastapi.testclient import TestClient
from app.main import app
from app.helpers.user_test_helper import UserTestHelper
from app.packages.geo.coordinate import Coordinate

client = TestClient(app)
user_test_helper = UserTestHelper(client=client)

def test_sort_by_rating_desc():
    response = client.get("/search/restaurants?sort_by=rating_desc")
    assert response.status_code == 200
    data = response.json()["data"] 

    if len(data) > 1: #if we have more than 1 restaurant, we can check the sorting, otherwise we can't really say if it's sorted or not
        assert data[0]["rating"] >= data[1]["rating"]

def test_sort_by_price_asc():
    response = client.get("/search/restaurants?sort_by=price_asc")
    assert response.status_code == 200
    data = response.json()["data"]

    if len(data) > 1: #here we check if the price is sorted low to high, but again only if we have more than 1 restaurant in the results
        assert data[0]["price_tier"] <= data[1]["price_tier"]

def test_sort_by_distance_asc():
    user_create = user_test_helper.test_user_create.model_copy()
    user_create.coordinate = Coordinate(0, 0)
    user_test_helper.register_and_login_user(user=user_create)
    
    response = client.get("/search/restaurants?sort_by=distance_asc", headers={"Authorization": f"Bearer {user_test_helper.login_token}"})
    assert response.status_code == 200
    restaurants = response.json()["data"]
    
    if len(restaurants) > 1: #if we have more than 1 restaurant, we can check the sorting, otherwise we can't really say if it's sorted or not
        sorted_restaurants = sorted(
            restaurants, 
            key=lambda r: float(Coordinate(**r.get("coordinate")).get_kilometer_distance_to(user_create.coordinate)), 
            reverse=False
        )

        print("\nAPI Order:", [r["name"] for r in restaurants])
        print("Test Order:", [r["name"] for r in sorted_restaurants])

        assert restaurants == sorted_restaurants
