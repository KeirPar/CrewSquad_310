from pathlib import Path
import json, os
from typing import List, Dict, Any

#had to change this file from what is originally in the repo because I wanted to have a more robust way of handling the data, and I also wanted to be able to update only certain fields without having to provide all of them, so I made all fields optional in the update model
class RestaurantRepository:
    def __init__(self):
        self.data_path = Path(__file__).resolve().parents[0] / "data" / "restaurant.json" #this points to our restaurant.json file
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
