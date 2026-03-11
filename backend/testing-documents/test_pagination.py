from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pagination_limit():

    response = client.get("/search/restaurants?limit=2") #testing with max limit 2
    
    assert response.status_code == 200
    data = response.json()["data"]
    
    assert len(data) == 2 #verying that we only get 2 results back, even if there are more that match the criteria in the JSON file

def test_pagination_offset_out_of_bounds():
    response = client.get("/search/restaurants?offset=100") #testing with an offset that is larger than the number of restaurants in the JSON file, this should return an empty list
    
    assert response.status_code == 200
    data = response.json()["data"]
    
    assert len(data) == 0 #make sure it doesnt crash, but just returns an empty list
    assert response.json()["message"] == "No restaurants found matching your criteria."