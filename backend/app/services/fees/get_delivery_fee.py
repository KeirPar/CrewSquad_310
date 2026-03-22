#   Get delivery fee based on distance between the restaurant and delivery address.
def get_delivery_fee(distanceInKilometers: float) -> float:
    if distanceInKilometers > 20:
        return 5.99
    
    if distanceInKilometers > 10:
        return 3.99
    
    return 1.99