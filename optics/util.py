"""
The Winding Number algorithm determines whether a point lies inside a polygon by calculating how many times the polygon winds around the point.

Algorithm Description
    - For each edge of the polygon, compute the angle subtended at P(x,y).
    - Sum these angles; if the total is 2π, P lies inside; if 0, P lies outside.
"""
from sympy import N, pi, Point2D, Ray as SympyRay, Line2D, Segment2D, atan2

from conf import ROUNDING_PRECISION


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
    return round(float(value), ROUNDING_PRECISION)


def deg2rad(deg):
    return deg * (pi / 180.0)

def rad2deg(rad):
    return rad * (180.0 / pi)

def round_point(point: Point2D):
    return Point2D(round_and_float(point.x), round_and_float(point.y))

def round_ray(ray: SympyRay):
    return SympyRay(round_point(ray.source), round_point(ray.p2))

def round_segment(segment: Segment2D):
    return Segment2D(round_point(segment.p1), round_point(segment.p2))

def round_line(line: Line2D):
    return Line2D(round_point(line.p1), round_point(line.p2))

def angle_to_ox(obj: Line2D | Segment2D | SympyRay):
    dx = obj.p2.x - obj.p1.x
    dy = obj.p2.y - obj.p1.y
    theta = atan2(dy, dx)
    return theta
