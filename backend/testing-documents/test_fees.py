import pytest
from app.services.fees.get_province_tax import get_province_tax
from app.services.fees.tax_type import TaxType
from app.services.fees.province_tax import ProvinceTax
from app.services.fees.get_container_recycling_fee import get_container_recycling_fee
from app.services.fees.get_delivery_fee import get_delivery_fee

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


def test_get_container_recycling_fee():
    assert get_container_recycling_fee() == 0.1

def test_get_delivery_fee():
    assert get_delivery_fee(0) == 1.99
    assert get_delivery_fee(12) == 3.99
    assert get_delivery_fee(100) == 5.99