from math import sqrt

def distance(lat1, lon1, alt1, lat2, lon2, alt2):
    return sqrt((lat2-lat1)**2 + (lon2-lon1)**2 + (alt2-alt1)**2)