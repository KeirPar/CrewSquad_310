from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User
from app.services.auth_service import AuthService
from app.schemas.payment import PaymentDecision, PaymentStatus
from app.services.payment_service import process_payment, simulate_payment
from fastapi import status


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/{order_id}")
def decide_payment(order_id: int, body: PaymentDecision, current_user: User = Depends(AuthService.get_current_user)):
    """
    Endpoint to process a payment decision for a given order.

    Args:
        order_id (int): The ID of the order for which the payment decision is being made.
        body (PaymentDecision): The payment decision details, including the decision and an optional reason.

    Returns:
        dict: A dictionary containing the updated payment attempt and order details after processing the decision.
    """
    if body.decision == PaymentStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment decision cannot be PENDING.")
    
    try:
        result = process_payment(
            order_id = order_id,
            decision = body.decision,
            user_id = current_user.id,
            reason = body.reason
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return result

@router.post("/{order_id}/simulate")
def simulate_payment_outcome(order_id: int, current_user: User = Depends(AuthService.get_current_user)):
    try:
        result = simulate_payment(
            order_id=order_id, 
            user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return result
