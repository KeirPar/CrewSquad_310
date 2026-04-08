from app.schemas.order import Order
from .user_repository import user_db
from pathlib import Path
import json, os
from typing import List, Dict, Optional, Any


class OrderRepository:
    
    def __init__(self):
        self.data_path = Path(__file__).resolve().parents[1] / "data" / "orders.json" #same as restaurant repo but for orders
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> List[Dict[str, Any]]: #grab all data from json
        if not self.data_path.exists():
            return []
            
        with self.data_path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_all(self, items: List[Dict[str, Any]]) -> None: #save all data to json
        tmp = self.data_path.with_suffix(".tmp")
        
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
            
        os.replace(tmp, self.data_path)

    def get_all_orders(self) -> List[Order]:
        return [Order(**o) for o in self.load_all()] #returning as order objects instead of dicts

    def next_id(self) -> int: #for adding new order, just make next id one higher than max
        orders = self.load_all()

        if len(orders) == 0:
            return 1 
        all_ids = [order["id"] for order in orders]
        highest_id = max(all_ids)
        return highest_id + 1
    
    def save(self, order: Order) -> None:
        orders = self.load_all()
        order_dict = order.model_dump(mode='json') #convert order object to dict for saving
        
        for i, o in enumerate(orders):
            if o["id"] == order.id:
                orders[i] = order_dict
                self.save_all(orders)
                return
        
        orders.append(order_dict)
        self.save_all(orders)

    def find_by_id(self, order_id: int) -> Optional[Order]:
        orders = self.load_all()
        for o in orders:
            if o["id"] == order_id:
                return Order(**o) #return order as object
        return None
    
    def find_all_by_user_id(self, user_id: int) -> List[Order]: #returning list of order for a specific user
        all_orders_by_user_id = []
        
        user = user_db.find_by_user_id(user_id)
        if not user:
            return []
            
        order_ids = user.order_history
        orders = self.load_all()
        
        for o in orders:
            if o["id"] in order_ids:
                all_orders_by_user_id.append(Order(**o)) 
                
        return all_orders_by_user_id 


order_db = OrderRepository()