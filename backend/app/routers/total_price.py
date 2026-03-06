from fastapi import APIRouter

router = APIRouter()

@router.get("/checkout/total-price")
def get_total_price(
    items_price: float,
    delivery_fee: float,
    disacountPercentage: float, 
    discount: float
) -> float:
    tax_percentage = 0.12
    return (items_price * (1 - disacountPercentage) - discount) * (1 - tax_percentage) + delivery_fee
  