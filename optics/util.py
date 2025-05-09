"""
The Winding Number algorithm determines whether a point lies inside a polygon by calculating how many times the polygon winds around the point.

Algorithm Description
    - For each edge of the polygon, compute the angle subtended at P(x,y).
    - Sum these angles; if the total is 2π, P lies inside; if 0, P lies outside.
"""
from sympy import N, pi


def is_point_inside_polygon(point, polygon):
    x, y = point
    wn = 0  # Winding number

    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        if y1 <= y:
            if y2 > y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) > 0:
                wn += 1
        else:
            if y2 <= y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) < 0:
                wn -= 1
    return wn != 0


def round_and_float(value):
    return round(float(N(value)), 2)


def deg2rad(deg):
    return deg * (pi / 180.0)

def rad2deg(rad):
    return rad * (180.0 / pi)