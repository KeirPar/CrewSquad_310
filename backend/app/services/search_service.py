from app.repositories.restaurant_repo import RestaurantRepository #import our repository
from app.schemas.restaurant_sort_order import RestaurantSortOrder

class SearchService: #make our SearchService class

    def __init__(self):
        self.repo = RestaurantRepository()

    def filter_restaurants(self, name: str = None, cuisine_type: str = None, min_rating: float = None, sort_by: RestaurantSortOrder = None, limit: int = 10, offset: int = 0):
        restaurants = self.repo.load_all() #get the data from the json
        if name: #name filter
            restaurants = [r for r in restaurants if name.lower() in r.get("name", "").lower()]
            
        if cuisine_type: #cuisine type filter
            restaurants = [r for r in restaurants if cuisine_type.lower() == r.get("cuisine_type", "").lower()]
            
        if min_rating is not None: #rating filter
            restaurants = [r for r in restaurants if r.get("rating", 0.0) >= min_rating]

        #added for sorting, we can sort by rating or price
        if sort_by == RestaurantSortOrder.RATING_DESC:
            restaurants.sort(key=lambda r: r.get("rating", 0.0), reverse=True) #sort by rating, high to low
        elif sort_by == RestaurantSortOrder.PRICE_ASC:
            restaurants.sort(key=lambda r: r.get("price_tier", 9999), reverse=False) #sort by price, low to high


        paginated_restaurants = restaurants[offset:offset + limit] 

        if len(paginated_restaurants) == 0: 
            return { #if the list is empty, return a message saying no restaurants found matching criteria, and an empty list for data
                "message": "No restaurants found matching your search. Try adjusting your filters or checking for typos.",  #I just made a small change to this message to make it a bit more helpful
                "data": []
            }

        #but if we made it here that means we have some results to return, so we return a success message and the paginated list of restaurants
        return {
            "message": "Success", 
            "data": paginated_restaurants
        }