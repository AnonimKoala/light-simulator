import sympy as sp
from .Geometry import Straight, Figure, Point


class Ray(Figure):
    """
    The `Ray` class represents a light ray and provides methods for its creation and operations.
    """

    def __init__(self, a, b, start_point):
        """
        Initializes an instance of the `Ray` class.

        :param a: Coefficient of the line equation
        :type a: float

        :param b: Coefficient of the line equation
        :type b: float

        :param start_point: Coordinates of the ray's starting point
        :type start_point: Point
        """
        super().__init__(a, b)

        # Equation of the ray in the form of a sympy Eq object
        self.eq = sp.Eq(a * Figure.x + b, Figure.y)

        # Starting point of the ray
        self.startPoint = start_point

        # Ending point of the ray, initially set to None
        self.endPoint = None

    def getEq(self):
        """
        Returns the equation of the ray's line.

        :return: Equation of the line
        :rtype: sympy.Eq
        """
        return self.eq

    def getStartPoint(self):
        """
        Returns the starting point of the ray.

        :return: Starting point
        :rtype: Point
        """
        return self.startPoint

    def getEqCoefficient(self):
        """
        Returns the coefficients of the ray's line equation, a and b.

        :return: Dictionary with coefficients a and b
        :rtype: dict(a: float, b: float)
        """
        return {'a': self.a, 'b': self.b}

    def setEndPoint(self, point):
        """
        Sets the endpoint of the ray.

        :param point: Endpoint of the ray
        :type point: Point
        """
        self.endPoint = point

    def getEndPoint(self):
        """
        Returns the endpoint of the ray.

        :return: Endpoint of the ray
        :rtype: Point
        """
        return self.endPoint

    @staticmethod
    def getRayAtPointWithAngle(point, angle):
        """
        Returns a ray passing through the given point and inclined at the specified angle to the OX axis.

        :param point: Point through which the ray passes
        :type point: Point

        :param angle: Angle of inclination to the OX axis
        :type angle: float

        :return: Ray
        :rtype: Ray
        """

        straight = Straight.getStraightAtPointWithAngle(point.x, point.y, angle)
        return Ray(straight.a, straight.b, point)
