from app.repositories.restaurant_repo import RestaurantRepository #import our repository


class SearchService: #make our SearchService class

    def __init__(self):
        self.repo = RestaurantRepository()

    def filter_restaurants(self, name: str = None, cuisine_type: str = None, min_rating: float = None):
        restaurants = self.repo.load_all() #get the data from the json
        if name: #name filter
            restaurants = [r for r in restaurants if name.lower() in r.get("name", "").lower()]
            
        if cuisine_type: #cuisine type filter
            restaurants = [r for r in restaurants if cuisine_type.lower() == r.get("cuisine_type", "").lower()]
            
        if min_rating is not None: #rating filter
            restaurants = [r for r in restaurants if r.get("rating", 0.0) >= min_rating]

        message = "Success" if restaurants else "No restaurants found matching your criteria."
        return {"message": message, "data": restaurants}