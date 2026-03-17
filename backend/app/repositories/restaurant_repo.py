from pathlib import Path
import json, os
from typing import List, Dict, Any

#had to change this file from what is originally in the repo because I wanted to have a more robust way of handling the data, and I also wanted to be able to update only certain fields without having to provide all of them, so I made all fields optional in the update model
class RestaurantRepository:
    def __init__(self):
        self.data_path = Path(__file__).resolve().parents[1] / "data" / "restaurant.json" #this points to our restaurant.json file
        self.data_path.parent.mkdir(parents=True, exist_ok=True)        #ensures that this exists, if not it creates it


    def load_all(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
                    return []
                
        with self.data_path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Returns empty if the file exists but is empty/corrupted
                return []

    def save_all(self, items: List[Dict[str, Any]]) -> None: #this saves all the restaurants to the json file
            tmp = self.data_path.with_suffix(".tmp")
            
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
                
            os.replace(tmp, self.data_path)         #this should just replace the old file with the new file, also its atomic :)


    def add_menu_item(self, restaurant_id: int, item_data: dict) -> dict:
        """Finds the restaurant, creates a new dish, and persists to JSON."""
        restaurants = self.load_all()
        for r in restaurants:
            if r["id"] == restaurant_id:
                #Check if the menu list exists
                if "menu" not in r:
                    r["menu"] = []
                
                #Get a unique ID for the dish
                new_id = max([item["id"] for item in r["menu"]], default=0) + 1 #updated this to make sure primary key integrity is upheld
                
                #Merge the IDs with the user data
                full_item = {
                    "id": new_id,
                    "restaurant_id": restaurant_id,
                    **item_data
                }
                
                r["menu"].append(full_item)
                self.save_all(restaurants)
                return full_item
        return None
    
    def update_menu_item(self, restaurant_id: int, item_id: int, update_data: dict) -> dict:
        """Finds a menu item within a restaurant and updates it."""
        restaurants = self.load_all()
        for r in restaurants:
            if r["id"] == restaurant_id:
                for item in r.get("menu", []):
                    if item["id"] == item_id:
                        #Apply said updates
                        for key, value in update_data.items():
                            item[key] = value
                        self.save_all(restaurants)
                        return item
        return None

    def delete_menu_item(self, restaurant_id: int, item_id: int) -> bool:
        """Deletes a menu item from a restaurant's menu."""
        restaurants = self.load_all()
        for r in restaurants:
            if r["id"] == restaurant_id:
                initial_len = len(r.get("menu", []))
                r["menu"] = [item for item in r["menu"] if item["id"] != item_id]
                
                if len(r["menu"]) < initial_len:
                    self.save_all(restaurants)
                    return True
        return False
    #create new restaurant
    def create_restaurant(self, restaurant_data: dict) -> dict:
        """Assigns a unique ID and saves a new restaurant to the JSON file."""
        restaurants = self.load_all()
        
        #Ensure we don't have id collisions
        new_id = max([r["id"] for r in restaurants], default=0) + 1
        
        #Create with an empty menu to put in later
        new_restaurant = {
            "id": new_id,
            "menu": [],
            **restaurant_data
        }
        
        restaurants.append(new_restaurant)
        self.save_all(restaurants)
        return new_restaurant
    
    #makes it so we can update the restaurant that we have created
    def update_restaurant(self, restaurant_id: int, update_data: dict) -> dict:
        """Updates restaurant metadata while keeping the menu intact."""
        restaurants = self.load_all()
        for r in restaurants:
            if r["id"] == restaurant_id:
                for key, value in update_data.items():
                    if key not in ["id", "menu"]:
                        r[key] = value
                self.save_all(restaurants)
                return r
        return None
    
#deletes restaurant and cascades making sure nothing else is left behind, done for Feat2-FR4
    def delete_restaurant(self, restaurant_id: int) -> bool:
        """Deletes a restaurant and its entire nested menu (Cascade Delete)."""
        restaurants = self.load_all()
        initial_len = len(restaurants)
        
        #Filter out the target restaurant, this deletes data as its nested
        restaurants = [r for r in restaurants if r["id"] != restaurant_id]
        
        if len(restaurants) < initial_len:
            self.save_all(restaurants)
            return True
        return False
