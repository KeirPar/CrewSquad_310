from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, UserRole
from app.schemas.admin import Admin
from app.services.auth_service import AuthService
from app.repositories.user_repository import user_db
from app.schemas.delivery_system_configuration import DeliverySystemConfiguration
from app.repositories.delivery_system_configuration_repo import delivery_system_configuration

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin(current_user: User = Depends(AuthService.get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can access.")
    return current_user

@router.post("/config/update")
def update_config(configuration: DeliverySystemConfiguration, admin: User = Depends(get_admin)) -> DeliverySystemConfiguration:
    global delivery_system_configuration

    delivery_system_configuration = configuration

    return delivery_system_configuration