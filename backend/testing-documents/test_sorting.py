from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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