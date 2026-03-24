from fastapi import APIRouter, Depends
from typing import Optional             #import all the stuff we need for the router and the service
from app.schemas.restaurant import SearchResponse, CuisineType
from app.services.search_service import SearchService
from app.services.auth_service import AuthService, oauth2_scheme
from app.schemas.restaurant_sort_order import RestaurantSortOrder
from app.schemas.user import User

router = APIRouter(prefix="/search", tags=["Search"]) #make sure the router is setup
search_service = SearchService()

@router.get("/restaurants", response_model=SearchResponse)
def search_restaurants(
    name: Optional[str] = None,
    cuisine_type: Optional[CuisineType] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[RestaurantSortOrder] = None, #how we're gonna sort (price or rating)
    limit: int = 10, #search return limit
    offset: int = 0 #search return offset
    # user: User = Depends(AuthService.get_current_user)
):
    #   Get current user
    user: Optional[User]
    try:
        user = AuthService.get_current_user(token=oauth2_scheme)
    except Exception as e:
        user = None
    
    # Pass the query parameters down to the service layer
    return search_service.filter_restaurants(
        name=name, 
        cuisine_type=cuisine_type, 
        min_rating=min_rating,
        sort_by=sort_by, #added this for the sorting
        from_coordinate=user.coordinate if user is not None else None,
        limit=limit, #added these 2 parameters to the service call
        offset=offset
    )