from sympy import Point2D
from optics.BasicObject import BasicObject


class Solver:
    optical_objects: list[BasicObject] = []
    lasers = []
    @staticmethod
    def find_first_collision(ray) -> Point2D|None:
        """
        Detects the collision of a ray with optical objects.
        :param ray: The ray to check for collisions
        :type ray: RayController
        """
        collision_points = []
        for obj in Solver.optical_objects:
            if collision_point := obj.get_collision(ray):
                collision_points.append(collision_point)

        if collision_points:
            return Solver.nearest_to_origin(ray.start_point, collision_points)
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



