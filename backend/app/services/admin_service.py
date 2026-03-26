from app.repositories.user_repository import user_db
from .auth_service import AuthService
from app.schemas.admin import Admin
from app.schemas.user import UserRole
from app.packages.geo.coordinate import Coordinate

class AdminService:
    admin_email = "admin@example.com"
    admin_password = "dOyOUkNOWiMaNaDMIN?"

    @classmethod
    def create_admins(cls):
        admin = Admin(
            id = len(user_db.get_all()) + 1,
            name = "Root",
            email = cls.admin_email,
            phone_number = "1234567",
            password_hash = AuthService.hash_password(cls.admin_password),
            role = UserRole.ADMIN,
            address = "",
            coordinate = Coordinate(0, 0),
            order_history = [],
            cart = [],
            admin_level=1
        )
    
        user_db.save(admin)