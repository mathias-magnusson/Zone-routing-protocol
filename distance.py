from math import cos, asin, sqrt, pi

"""def distance(lat1, lon1, lat2, lon2):
    r = 6371+718 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))"""

def distance(lat1, lon1, alt1, lat2, lon2, alt2):
    return sqrt((lat2-lat1)**2 + (lon2-lon1)**2 + (alt2-alt1)**2)