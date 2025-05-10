from sympy import Point2D, Segment2D, Line2D, Ray
from optics.BasicController import BasicController
from optics.util import round_point, round_and_float, rad2deg


class Solver:
    optical_objects: list[BasicController] = []
    lasers = []
    OX = Line2D(Point2D(0, 0), Point2D(1, 0))
    @staticmethod
    def find_first_collision(ray: Ray) -> dict[str, Point2D | Segment2D] | None:
        """
        Detects the collision of a ray with optical objects.
        :param ray: The ray to check for collisions
        :type ray: Ray
        """
        collisions = []
        for obj in Solver.optical_objects:
            if collision_data := obj.get_collision(ray):
                collisions.append(collision_data)
        if collisions:
            nearest = min(collisions, key=lambda cp: cp["point"].distance(round_point(ray.source)))
            nearest["point"] = round_point(nearest["point"])
            return nearest
        return None

    @staticmethod
    def nearest_to_origin(origin, objs):
        """
        Finds the nearest object to the origin.
        :param origin: The origin point
        :type origin: Point2D
        :param objs: List of objects to check
        :type objs: list[Point2D]
        :return: The nearest object to the origin
        """
        return min(objs, key=lambda obj: obj.distance(origin))

    @staticmethod
    def get_refractions(ray: Ray, collisions: list[Point2D]) -> list[Point2D] | None:
        collisions = []
        def func(ray1: Ray):
            if collision := Solver.find_first_collision(ray1):
                normal_angle_to_ox = Solver.OX.smallest_angle_between(collision["normal"])
                new_ray_angle_to_ox = 2 * normal_angle_to_ox - Solver.OX.smallest_angle_between(ray1)
                new_ray = Ray(collision["point"],  angle=new_ray_angle_to_ox)
                return Ray(round_point(new_ray.source),  round_point(new_ray.p2))
            return None
        while ray := func(ray):
            collisions.append(round_point(ray.source))
        return collisions

    @staticmethod
    def first_intersection(ray: Ray, obj) -> Point2D | None:
        if intersections := ray.intersection(obj):
            nearest = Solver.nearest_to_origin(round_point(ray.source), intersections)
            if isinstance(nearest, Segment2D):
                return round_point(Solver.nearest_to_origin(round_point(ray.source), [nearest.p1, nearest.p2]))
            return round_point(nearest)
        return None
