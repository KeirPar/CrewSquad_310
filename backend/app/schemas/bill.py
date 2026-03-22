from pydantic import BaseModel
from app.services.fees.tax_type import TaxType

class Bill(BaseModel):
    items_subtotal: float
    taxes: list[tuple[TaxType, float]]
    # container_recycling_fee: float
    delivery_fee: float

    def get_total_tax(self) -> float:
        total_tax = 0

        for tax in self.taxes:
            total_tax += tax[1]
        return total_tax

    def get_total(self) -> float:
        return self.items_subtotal + self.get_total_tax() + self.delivery_fee
    
    @classmethod
    def empty(cls):
        return cls(items_subtotal=0, taxes=[], delivery_fee=0)