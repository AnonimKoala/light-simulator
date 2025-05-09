from sympy import Point2D
from optics.BasicController import BasicController


class Solver:
    optical_objects: list[BasicController] = []
    lasers = []
    @staticmethod
    def find_first_collision(ray) -> dict[str, Point2D | BasicController] | None:
        """
        Detects the collision of a ray with optical objects.
        :param ray: The ray to check for collisions
        :type ray: RayController
        """
        collisions = []
        for obj in Solver.optical_objects:
            if collision_data := obj.get_collision(ray):
                collisions.append(collision_data)

        if collisions:
            return min(collisions, key=lambda cp: cp["point"].distance(ray.start_point))
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



