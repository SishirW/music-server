import math


def get_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth's surface
    using the Haversine formula.

    Parameters:
        lat1, lon1: Latitude and longitude of the first point in degrees.
        lat2, lon2: Latitude and longitude of the second point in degrees.

    Returns:
        Distance between the two points in kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences in latitude and longitude
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * \
        math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the distance
    distance_km = R * c

    # Convert the distance to meters
    distance = distance_km * 1000

    return distance


def get_location_from_header(request):
    location = {
        "lat": float(request.headers['lat']),
        "long": float(request.headers['long']),
    }
    return location
