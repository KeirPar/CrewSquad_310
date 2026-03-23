from typing import List, Optional
from app.schemas.user import User

class UserRepository:
    
    def __init__(self):
        self._users: List[User] = []

    def save (self, user: User) -> User:
        """Adds user to storage"""
        self._users.append(user)
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Returns a user by email or returns none if not found."""
        return next((u for u in self._users if u.email == email), None)
    
    def find_by_user_id(self, user_id: int) -> Optional[User]:
        for user in self._users:
            if user_id == user.id:
                return user
        return None
    
    def find_by_cart_id(self, cart_id: int) -> Optional[User]:
        for user in self._users:
            if cart_id in user.cart:
                return user
        return None
    
    def find_by_order_id(self, order_id: int) -> Optional[User]:
        for user in self._users:
            if order_id in user.order_history:
                return user
        return None
    
    def get_all(self) -> List[User]:
        """Return all registered users"""
        return self._users
    

user_db = UserRepository()