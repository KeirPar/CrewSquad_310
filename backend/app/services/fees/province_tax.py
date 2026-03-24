from .tax_type import TaxType

#   Tax rates by catagory(TaxType) of a province.
class ProvinceTax:
    tax_rates: list[tuple[TaxType, float]]

    def __init__(self, taxes: list[tuple[TaxType, float]]):
        self.tax_rates = taxes

    def get_total_tax_rate(self) -> float:
        result = 0.0
        for tax in self.tax_rates:
            result += tax[1]
        return result
    
    def __eq__(self, value):
        if not isinstance(value, ProvinceTax):
            return NotImplemented
        return value.tax_rates == self.tax_rates