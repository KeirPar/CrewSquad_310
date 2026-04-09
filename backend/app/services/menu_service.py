from app.schemas import restaurant
from app.repositories.restaurant_repo import RestaurantRepository
from app.schemas.menu_item import MenuItem


class MenuService:
    def __init__(self):
        self.repo = RestaurantRepository() #grab the restaurants

    def get_all_menu_items(self) -> list[MenuItem]:
        restaurant = self.repo.load_all() #load all data
        
        all_items = []
        for r in restaurant:
            all_items.extend([MenuItem(**raw_menu) for raw_menu in r.get("menu", [])]) #grab menus

        return all_items

    def get_menu_items(self, limit: int, offset: int) -> dict:

        restaurant = self.repo.load_all() #load all data
        
        all_items = []
        for r in restaurant:
            all_items.extend(r.get("menu", [])) #grab menus

        total_items = len(all_items)
        selected_items = all_items[offset:offset + limit] #add offset and limit

        return { #return data
            "total_items": total_items,
            "limit": limit,
            "offset": offset,
            "items": selected_items
        }

menu_service = MenuService() #create an instance of the service to be used in the router