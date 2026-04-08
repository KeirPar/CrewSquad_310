from fastapi import APIRouter, HTTPException, Depends
from app.schemas.scheduled_order import ScheduledOrderCreate, ScheduledOrder
from app.schemas.user import User
from app.services.auth_service import AuthService
from app.services.scheduled_service import (
    create_scheduled_order,
    cancel_scheduled_order,
    get_my_scheduled_orders,
    get_scheduled_order_by_id
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/scheduled-orders", tags=["Scheduled Orders"])


class CancelRequest(BaseModel):
    """Optional request body for cancellation reason."""
    reason: Optional[str] = ""



@router.post("", status_code=201)
def place_scheduled_order(
    body: ScheduledOrderCreate,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Places a new scheduled order for a future delivery time."""
    try:
        return create_scheduled_order(body, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/my-orders/all")
def get_my_orders(
    current_user: User = Depends(AuthService.get_current_user)
):
    """ Returns all scheduled orders for the currently logged in user"""
    return get_my_scheduled_orders(current_user.id)



@router.get("/{scheduled_order_id}")
def get_scheduled_order(
    scheduled_order_id: int,
    current_user: User = Depends(AuthService.get_current_user)
):
    """
    Returns a specific scheduled order by ID (FR5).

    Raises:
        404 if the scheduled order is not found.
    """
    scheduled_order = get_scheduled_order_by_id(scheduled_order_id)
    if not scheduled_order:
        raise HTTPException(
            status_code=404,
            detail=f"Scheduled order {scheduled_order_id} not found."
        )
    return scheduled_order




@router.patch("/{scheduled_order_id}/cancel")
def cancel_order(
    scheduled_order_id: int,
    body: CancelRequest = CancelRequest(),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Cancels a scheduled order """
    try:
        return cancel_scheduled_order(
            scheduled_order_id=scheduled_order_id,
            user_id=current_user.id,
            reason=body.reason or ""
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))