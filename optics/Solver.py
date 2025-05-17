from sympy import Point2D, Segment2D, Line2D, Ray, Ray2D, pi, cos, sin

from conf import RAY_MAX_LENGTH, MAX_REFRACTIONS
from optics.BasicController import BasicController
from optics.util import round_point, round_ray, angle_to_ox


class Solver:
    optical_objects: list[BasicController] = []
    lasers = []
    OX = Line2D(Point2D(0, 0), Point2D(1, 0))

    @staticmethod
    def find_first_collision(ray: Ray2D) -> dict[str, Point2D | Segment2D] | None:
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
            # Filter out collisions that are the same as the ray source
            collisions = [cp for cp in collisions if round_point(cp["point"]) != round_point(ray.source)]
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
    def get_refractions(ray: Ray2D) -> list[Point2D] | None:
        collisions = []

        def compute_ray_reflection(incident_ray: Ray2D) -> Point2D | Ray2D:
            if collision := Solver.find_first_collision(incident_ray):
                normal_angle_to_ox = angle_to_ox(collision['normal'])
                new_ray_angle_to_ox = 2 * normal_angle_to_ox - angle_to_ox(incident_ray) + pi
                new_ray = round_ray(Ray2D(collision["point"], angle=new_ray_angle_to_ox))
                return round_ray(new_ray)
            return Solver.get_ray_inf_point(incident_ray)

        i = 0
        while True:
            i += 1
            result = compute_ray_reflection(ray)
            if isinstance(result, Ray):
                ray = result
                collisions.append(round_point(ray.source))
                if i > MAX_REFRACTIONS:
                    collisions.append(round_point(Solver.get_ray_inf_point(ray)))
                    break
            if isinstance(result, Point2D):
                collisions.append(round_point(result))
                break
        return collisions

    @staticmethod
    def first_intersection(ray: Ray, obj) -> Point2D | None:
        if intersections := ray.intersection(obj):
            nearest = Solver.nearest_to_origin(round_point(ray.source), intersections)
            if isinstance(nearest, Segment2D):
                return round_point(Solver.nearest_to_origin(round_point(ray.source), [nearest.p1, nearest.p2]))
            return round_point(nearest)
        return None

    @staticmethod
    def get_ray_inf_point(ray: Ray2D) -> Point2D:
        ray_angle = angle_to_ox(ray)
        end_x = ray.source.x + RAY_MAX_LENGTH * cos(ray_angle)
        end_y = ray.source.y + RAY_MAX_LENGTH * sin(ray_angle)
        return round_point(Point2D(end_x, end_y))
