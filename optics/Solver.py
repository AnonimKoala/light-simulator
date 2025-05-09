from sympy import Point2D, Segment2D, Line2D, Ray
from optics.BasicController import BasicController


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
            return min(collisions, key=lambda cp: cp["point"].distance(ray.source))
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
        print("start get_refractions")
        if collision := Solver.find_first_collision(ray):
            collisions.append(collision["point"])
            surface_angle = Solver.OX.smallest_angle_between(collision["surface"])
            beta = 2 * surface_angle - Solver.OX.smallest_angle_between(ray)
            print("Collision point: ",collision["point"])
            print("Source: ",ray.source)
            return Solver.get_refractions(Ray(collision["point"],  angle=beta+surface_angle), collisions)
        # collisions.append(Point2D(inf,inf))
        return collision

    @staticmethod
    def first_intersection(ray: Ray, obj) -> Point2D | None:
        if intersections := ray.intersection(obj):
            return Solver.nearest_to_origin(ray.source, intersections)
        return None
