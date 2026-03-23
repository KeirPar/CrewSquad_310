from math import radians, cos, sin, asin, sqrt
from pydantic import Field
from pydantic.dataclasses import dataclass

#   From: https://gist.github.com/amalgjose/6d760a7b963aaa64f734
def get_distance(lon1, lat1, lon2, lat2) -> float:
    ##convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    ##haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
    return c * r

@dataclass
class Coordinate:
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def get_kilometer_distance_to(self, other) -> float:
        return get_distance(
            self.longitude, self.latitude,
            other.longitude, other.latitude
        )