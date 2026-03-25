from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User
from app.schemas.order import Order
from app.services.auth_service import AuthService
from app.repositories.user_repository import user_db
from app.schemas.user import UserRole
from app.services.order_service import get_orders_by_distance

router = APIRouter(prefix="/driver", tags=["Delivery Driver"])

def get_delivery_driver(current_user: User = Depends(AuthService.get_current_user)):
    if current_user.role != UserRole.DELIVERY_DRIVER: #make sure user is delivery driver
            raise HTTPException(status_code=403, detail="Only delivery driver can access the pending orders queue.")
    return current_user

@router.get("/orders")
def get_orders(
    max_km: float, 
    delivery_driver: User = Depends(get_delivery_driver)
) -> list[Order]:
    return get_orders_by_distance(
        from_coordinate=delivery_driver.coordinate, 
        max_kilometer_distance=max_km
    )