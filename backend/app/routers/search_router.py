from fastapi import APIRouter
from typing import Optional             #import all the stuff we need for the router and the service
from app.schemas.restaurant import SearchResponse
from app.services.search_service import SearchService
from app.schemas.restaurant_sort_order import RestaurantSortOrder

router = APIRouter(prefix="/search", tags=["Search"]) #make sure the router is setup
search_service = SearchService()

@router.get("/restaurants", response_model=SearchResponse)
def search_restaurants(
    name: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[RestaurantSortOrder] = None, #how we're gonna sort (price or rating)
    limit: int = 10, #search return limit
    offset: int = 0 #search return offset 
    
):
    # Pass the query parameters down to the service layer
    return search_service.filter_restaurants(
        name=name, 
        cuisine_type=cuisine_type, 
        min_rating=min_rating,
        sort_by=sort_by, #added this for the sorting
        limit=limit, #added these 2 parameters to the service call
        offset=offset
    )