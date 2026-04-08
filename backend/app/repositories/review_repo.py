from typing import List
from app.schemas.review import Review
from pathlib import Path
import json, os
from typing import List, Dict, Optional, Any

class ReviewRepository:
    def __init__(self):
        self.data_path = Path(__file__).resolve().parents[1] / "data" / "reviews.json" 
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

    def get_all_reviews(self) -> List[Review]:
        return [Review(**r) for r in self.load_all()] #returning as review objects instead of dicts
    
    def save(self, review: Review) -> Review:
        # Auto-assign an ID if it's a brand new review
        if review.id == 0:
            review.id = self.next_id()
            
        reviews = self.load_all()
        review_dict = review.model_dump(mode='json') #convert review object to dict for saving
        
        for i, r in enumerate(reviews):
            if r["id"] == review.id:
                reviews[i] = review_dict
                self.save_all(reviews)
                return review # return the saved review
        
        reviews.append(review_dict)
        self.save_all(reviews)
        return review

    def find_by_id(self, review_id: int) -> Optional[Review]:
        reviews = self.load_all()
        for r in reviews:
            if r["id"] == review_id:
                return Review(**r) #return review as object
        return None
        
    def clear_all(self) -> None:
        self.save_all([])

    def next_id(self) -> int: #for adding new report, just make next id one higher than max
        reviews = self.load_all()

        if len(reviews) == 0:
            return 1 
        all_ids = [review["id"] for review in reviews]
        highest_id = max(all_ids)
        return highest_id + 1

review_db = ReviewRepository()