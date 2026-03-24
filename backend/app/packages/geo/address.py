from .canada_province import CanadaProvince

class Address():
    province: CanadaProvince
    city: str
    street_address: str
    apt: str    #   Apartment number