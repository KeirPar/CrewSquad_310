from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/user", tags = ["User"])

@router.post("/update")
def update_user(updated_user_data: UserCreate, user: User = Depends(AuthService.get_current_user)):
    user.name = updated_user_data.name
    user.email = updated_user_data.email
    user.phone_number = updated_user_data.phone_number
    user.password_hash = AuthService.hash_password(updated_user_data.password)
    user.role = updated_user_data.role
    user.address = updated_user_data.address
    user.delivery_note = updated_user_data.delivery_note
