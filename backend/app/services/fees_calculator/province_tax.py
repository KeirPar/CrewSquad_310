from .tax_type import TaxType

#   Tax rates by catagory(TaxType) of a province.
class ProvinceTax:
    taxes: list[tuple[TaxType, float]]

    def __init__(self, taxes: list[tuple[TaxType, float]]):
        self.taxes = taxes

    def get_total_tax_rate(self) -> float:
        result = 0.0
        for tax in self.taxes:
            result += tax[1]
        return result
    
    def __eq__(self, value):
        if not isinstance(value, ProvinceTax):
            return NotImplemented
        return value.taxes == self.taxes