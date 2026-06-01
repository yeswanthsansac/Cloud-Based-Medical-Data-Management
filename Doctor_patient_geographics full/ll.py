import math

def move_point(lat, lon, distance_m, bearing_deg):
    """
    Move a point given a distance and bearing.
    :param lat: original latitude in degrees
    :param lon: original longitude in degrees
    :param distance_m: distance to move in meters
    :param bearing_deg: direction in degrees (0 = North, 90 = East)
    :return: new latitude and longitude
    """
    R = 6378137  # Earth radius in meters
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(math.sin(lat1) * math.cos(distance_m / R) +
                     math.cos(lat1) * math.sin(distance_m / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance_m / R) * math.cos(lat1),
                             math.cos(distance_m / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)

# Example: Move 29 meters to the North
original_lat = 10.3579648
original_lon = 77.9845632
distance = 29  # meters.., distance can be changeable ..,change the distance 
bearing = 0  # North

29  # meters
# New Latitude: 10.358225311432397
# New Longitude: 77.9845632
# PS C:\Users\System3\Desktop\next sem project\Doctor_patient_geographics full> python ll.py
35  # meters
# New Latitude: 10.358279210349442
# New Longitude: 77.9845632



new_lat, new_lon = move_point(original_lat, original_lon, distance, bearing)
print("New Latitude:", new_lat)
print("New Longitude:", new_lon)
