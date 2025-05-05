import sympy as sp
from .Geometry import Point
from .LightRay import LightRay
from .OpticsSolver import OpticsSolver


class Laser:
    """
    The `Laser` class represents a light source/laser.
    """

    # Default size of the laser
    DEFAULT_SIZE = 1

    # Size proportions
    WIDTH = 16
    HEIGHT = 9

    # Thickness of a single ray
    RAY_SIZE = 0.2

    # Gap between rays
    RAY_GAP = 0.1

    def __init__(self, x, y, rotation=0):
        """
        Initializes an instance of the `Laser` class.

        :param x: X-coordinate
        :type x: float

        :param y: Y-coordinate
        :type y: float

        :param rotation: Inclination to the OX axis
        :type rotation: float
        """

        self.pos = Point(x, y)
        self.rotation = rotation

        self.width = Laser.DEFAULT_SIZE * Laser.WIDTH
        self.height = Laser.DEFAULT_SIZE * Laser.HEIGHT

        self.rays = []
        self.beamSize = 2
        self.calcRays()

        self.uid = OpticsSolver.getNextID()
        OpticsSolver.LASERS.append(self)

    def getRayShiftedPoint(self, distance=0):
        """
        Returns a point shifted from the center of the laser towards the edge by a given distance.

        :param distance: Shift relative to the center
        :type distance: float

        :return: Point
        :rtype: Point
        """

        if distance < 0:
            return Point(
                self.pos.x - (abs(distance) * sp.sin(self.rotation)),
                self.pos.y + (abs(distance) * sp.cos(self.rotation))
            )

        return Point(
            self.pos.x + (distance * sp.sin(self.rotation)),
            self.pos.y - (distance * sp.cos(self.rotation))
        )

    def getRayStartPoint(self, shifted_point):
        """
        Returns the point from which the ray originates.

        :param shifted_point: Point shifted relative to the center
        :type shifted_point: Point

        :return: Point
        :rtype: Point
        """
        moveX = self.height / 2 * sp.cos(self.rotation)
        moveY = self.height / 2 * sp.sin(self.rotation)

        return Point(
            shifted_point.x + moveX,
            shifted_point.y + moveY
        )

    def getRayFromPoint(self, start_point):
        """
        Returns the equation of the ray passing through the given point.

        Uses the formulas:
        a = tan(alpha)
        b = y - ax <- Substitutes the position of the laser for [x, y]

        :param start_point: Point where the ray starts
        :type start_point: Point

        :return: Ray
        :rtype: Ray
        """

        return LightRay(sp.tan(self.rotation * sp.pi / 180).evalf(), start_point.y - (sp.tan(self.rotation * sp.pi / 180).evalf() * start_point.x), start_point)

    def calcRays(self):
        """
        Calculates and updates the laser beam rays.
        """

        self.rays = []

        for i in range(self.beamSize):
            self.rays.append(
                self.getRayFromPoint(
                    self.getRayStartPoint(
                        self.getRayShiftedPoint(i * Laser.RAY_SIZE + Laser.RAY_GAP)
                    )
                )
            )
            self.rays.append(
                self.getRayFromPoint(
                    self.getRayStartPoint(
                        self.getRayShiftedPoint(i * Laser.RAY_SIZE * -1 - Laser.RAY_GAP)
                    )
                )
            )

    def setPos(self, x, y):
        """
        Sets the position of the laser and updates the beam rays.

        :param x: X-coordinate
        :type x: float

        :param y: Y-coordinate
        :type y: float
        """
        self.pos = Point(x, y)
        self.calcRays()

    def getPos(self):
        """
        Returns the position of the laser.

        :return: Position of the laser
        :rtype: Point
        """
        return self.pos

    def setRotation(self, rotation):
        """
        Sets the rotation of the laser and updates the beam rays.

        :param rotation: Inclination to the OX axis
        :type rotation: float
        """
        self.rotation = rotation
        self.calcRays()

    def getRayEqsList(self):
        """
        Returns a list of equations of the beam rays.

        :return: List of equations
        :rtype: list[sympy.Eq]
        """
        eqs = []
        for ray in self.rays:
            eqs.append(ray.eq)
        return eqs

    def getRays(self):
        """
        Returns a list of beam rays.

        :return: List of rays
        :rtype: list[Ray]
        """
        return self.rays

    def setSize(self, scale=1):
        """
        Sets the size of the laser (as a light source).

        :param scale: Scale
        :type scale: float
        """
        self.width = Laser.DEFAULT_SIZE * Laser.WIDTH * scale
        self.height = Laser.DEFAULT_SIZE * Laser.HEIGHT * scale
        self.calcRays()

    def setBeamSize(self, size=1):
        """
        Sets the beam thickness, i.e., (half - 1) the number of rays in the beam.

        :param size: Beam thickness
        :type size: int
        """
        self.beamSize = size
        self.calcRays()
