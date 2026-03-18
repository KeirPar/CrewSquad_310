from app.schemas import restaurant
from app.repositories.restaurant_repo import RestaurantRepository


class MenuService:
    def __init__(self):
        self.repo = RestaurantRepository()

    def get_menu_items(self, limit: int, offset: int) -> dict:

        restaurant = self.repo.load_all() 
        
        menu_items = restaurant.get("menu", [])
        total_items = len(menu_items)
        selected_items = menu_items[offset:offset + limit]

        return {
            "total_items": total_items,
            "limit": limit,
            "offset": offset,
            "items": selected_items
        }