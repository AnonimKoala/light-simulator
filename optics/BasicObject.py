from abc import ABC, abstractmethod

class BasicObject(ABC):
    """
    BasicObject is a base class for all objects in the optics engine.
    It provides a common interface for all objects that interact with light.
    """

    @abstractmethod
    def get_collision_point(self, ray):
        pass
