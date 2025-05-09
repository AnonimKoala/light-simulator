from abc import ABC, abstractmethod

from sympy import Point2D


class BasicController(ABC):
    """
    BasicController is a base class for all objects in the optics engine.
    It provides a common interface for all objects that interact with light.
    """

    @abstractmethod
    def get_collision(self, ray) -> Point2D | None:
        """
        Detects the collision of a ray with the object.
        :param ray: The ray to check for collisions with
        :type ray: RayController
        :return: List of collision points
        """
        pass
