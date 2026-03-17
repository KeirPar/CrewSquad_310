from fastapi import APIRouter, HTTPException
from app.schemas.payment import PaymentDecision, PaymentStatus
from app.services.payment_service import process_payment


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/{order_id}")
def decide_payment(order_id: int, body: PaymentDecision):
    """
    Endpoint to process a payment decision for a given order.

    Args:
        order_id (int): The ID of the order for which the payment decision is being made.
        body (PaymentDecision): The payment decision details, including the decision and an optional reason.

    Returns:
        dict: A dictionary containing the updated payment attempt and order details after processing the decision.
    """
    if body.decision == PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment decision cannot be PENDING.")
    
    try:
        result = process_payment(
            order_id = order_id,
            decision = body.decision,
            reason = body.reason
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return result
