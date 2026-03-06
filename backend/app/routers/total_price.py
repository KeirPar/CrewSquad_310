from fastapi import APIRouter

router = APIRouter()

@router.get("/checkout/total-price")
def get_total_price(
    items_price: float,
    delivery_fee: float = 0,
    disacountPercentage: float = 0, 
    discount: float = 0
) -> float:
    tax_percentage = 0.12
    result = items_price
    result *= 1 - disacountPercentage
    result - discount
    result *= 1 + tax_percentage
    result += delivery_fee
    result = max(0, result)
    return result