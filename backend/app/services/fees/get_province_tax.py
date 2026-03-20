from .tax_type import TaxType
from .province_tax import ProvinceTax

#   Province and its corresponding tax rates 
#   Used data from "https://www.queensu.ca/financialservices/sites/finswww/files/uploaded_files/Procedures/Printable%20Tax%20Rates%20by%20Provinces_1.pdf".
province_tax_by_provice_code: dict[str, ProvinceTax] = {
    "ON" : ProvinceTax([
        (TaxType.GST, 0.13),
    ]),
    "NB" : ProvinceTax([
        (TaxType.GST, 0.15),
    ]),
    "NS" : ProvinceTax([
        (TaxType.HST, 0.14),
    ]),
    "PE" : ProvinceTax([
        (TaxType.HST, 0.15),
    ]),
    "BC" : ProvinceTax([
        (TaxType.GST, 0.05),
        (TaxType.PST, 0.07),
    ]),
    "MB" : ProvinceTax([
        (TaxType.GST, 0.05),
        (TaxType.PST, 0.07),
    ]),
    "SK" : ProvinceTax([
        (TaxType.GST, 0.05),
        (TaxType.PST, 0.06),
    ]),
    "QC" : ProvinceTax([
        (TaxType.PST, 0.0975),
    ]),
    "AB" : ProvinceTax([
        (TaxType.GST, 0.05),
    ]),
    "NT" : ProvinceTax([
        (TaxType.GST, 0.05),
    ]),
    "NU" : ProvinceTax([
        (TaxType.GST, 0.05),
    ]),
    "YT" : ProvinceTax([
        (TaxType.GST, 0.05),
    ]),
}

#   Get tax rates by province code.
#   Raises an error if the province code is invalid.
def get_province_tax(province_code: str) -> ProvinceTax:
    province_tax = province_tax_by_provice_code[province_code]

    return province_tax