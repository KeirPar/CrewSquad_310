import pytest
from app.services.taxes.tax_rate_calculator import get_province_tax
from app.services.taxes.tax_type import TaxType
from app.services.taxes.province_tax import ProvinceTax

#   Test getting the total tax rate and separate tax rates by a valid province code.
def test_tax_rates():
    province_code = "ON"
    province_tax = get_province_tax(province_code)
    assert province_tax.get_total_tax_rate() == 0.13
    assert province_tax == ProvinceTax([
        (TaxType.GST, 0.13),
    ])

#   Test getting the total tax rate and separate tax rates by a invalid province code.
def test_tax_rates_with_fake_province_code():
    with pytest.raises(KeyError):
        province_code = "FAKE"
        province_tax = get_province_tax(province_code)