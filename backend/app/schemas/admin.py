from pydantic import BaseModel
from app.schemas.user import User

class Admin(User):
    admin_level: int