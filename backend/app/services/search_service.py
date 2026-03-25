from app.repositories.restaurant_repo import RestaurantRepository #import our repository
from app.schemas.restaurant_sort_order import RestaurantSortOrder
from app.schemas.restaurant import CuisineType
from app.packages.geo.coordinate import Coordinate
from typing import Optional

class SearchService: #make our SearchService class

    def __init__(self):
        self.repo = RestaurantRepository() #make the repository so we can grab the data from the json

    def filter_restaurants(
        self, 
        name: str = None, 
        cuisine_type: CuisineType = None, 
        min_rating: float = None, 
        sort_by: RestaurantSortOrder = None, 
        from_coordinate: Optional[Coordinate] = None, 
        limit: int = 10, 
        offset: int = 0
    ):
        restaurants = self.repo.load_all() #get the data from the json
        if name: #name filter
            restaurants = [r for r in restaurants if name.lower() in r.get("name", "").lower()]
            
        if cuisine_type: #cuisine type filter, changed for enum
            restaurants = [r for r in restaurants if cuisine_type.value.lower() == r.get("cuisine_type", "").lower()]
            
        if min_rating is not None: #rating filter
            restaurants = [r for r in restaurants if r.get("rating", 0.0) >= min_rating]
        
        sort_error_message = ""
        #added for sorting, we can sort by rating or price
        if sort_by == RestaurantSortOrder.RATING_DESC:
            restaurants.sort(key=lambda r: r.get("rating", 0.0), reverse=True) #sort by rating, high to low
        elif sort_by == RestaurantSortOrder.PRICE_ASC:
            restaurants.sort(key=lambda r: float(r.get("price_tier", 9999)), reverse=False) #sort by price, low to high
        elif sort_by == RestaurantSortOrder.DISTANCE_ASC:
            if from_coordinate is None:
                sort_error_message = "No user coordinate provided, failed to sort restaurant by distance"
            else:
                restaurants.sort(
                    key=lambda r: float(Coordinate(**r.get("coordinate")).get_kilometer_distance_to(from_coordinate)) if r.get("coordinate") is not None else 9999999999999,
                    reverse=False
                ) 

        paginated_restaurants = restaurants[offset:offset + limit] #add the pagination (offset and limit)

        if len(paginated_restaurants) == 0: 
            return { #if the list is empty, return a message saying no restaurants found matching criteria, and an empty list for data
                "message": "No restaurants found matching your search. Try adjusting your filters or checking for typos.",  #I just made a small change to this message to make it a bit more helpful
                "data": []
            }
        
        #   When there's a sort error, return restaurants with the sort error message.
        if sort_error_message != "":
            return {
                "message": sort_error_message,
                "data": paginated_restaurants
            }

        #but if we made it here that means we have some results to return, so we return a success message and the paginated list of restaurants
        return {
            "message": "Success", 
            "data": paginated_restaurants
        }