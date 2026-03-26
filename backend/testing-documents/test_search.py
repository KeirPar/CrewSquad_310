from fastapi.testclient import TestClient
from app.main import app
from fastapi import status

client = TestClient(app)

def test_by_cuisine():
    response = client.get("/search/restaurants?cuisine_type=Mexican") #this should return all the restaurants that have mexican cuisine, if there are any
    assert response.status_code == status.HTTP_200_OK #check that the response is successful, same for other functions
    data = response.json()["data"] 

    if len(data) > 0: #if there are any restaurants returned, check that they all have mexican cuisine
            for restaurant in data:
                assert restaurant["cuisine_type"].lower() == "mexican"

def test_by_min_rating(): #this should return all the restaurants that have a rating of 4.0 or higher, if there are any
    response = client.get("/search/restaurants?min_rating=4.0")         #the min rating could be changed
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    
    if len(data) > 0: #if there are any restaurants returned, check that they all have a rating of 4.0 or higher
            for restaurant in data:
                assert restaurant["rating"] >= 4.0 #the rating threshold could be changed to whatever we want

def test_no_results(): #made small change here
    # Search for something that definitely doesn't exist
    response = client.get("/search/restaurants?cuisine_type=Other&min_rating=5.0") #this should return no results
    
    assert response.status_code == status.HTTP_200_OK

    assert response.json()["message"] == "No restaurants found matching your search. Try adjusting your filters or checking for typos." #made this same message in search_service
    assert len(response.json()["data"]) == 0