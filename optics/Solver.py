from optics.BasicObject import BasicObject


class Solver:
    optical_objects: list[BasicObject] = []

    @staticmethod
    def collision_detector(ray):
        """
        Detects the collision of a ray with optical objects.
        :param ray: The ray to check for collisions
        :type ray: RayController
        """

        for obj in Solver.optical_objects:
            if obj.get_collisions(ray):
                pass
