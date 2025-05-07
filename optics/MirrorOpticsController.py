from .BasicObject import BasicObject
from .Geometry import Point, Straight, Figure
from .Material import Material
from .OpticsSolver import OpticsSolver
import sympy as sp

from .Solver import Solver


class MirrorOpticsController(BasicObject):
    """
    The `Mirror` class allows the creation of mirrors.
    """

    DEF_WIDTH = 20
    DEF_HEIGHT = 60

    def __init__(self, x: float, y: float, width: float = DEF_WIDTH, height: float = DEF_HEIGHT):
        """
        Initializes an instance of the `Mirror` class.

        :param x: X-coordinate of the center
        :param y: Y-coordinate of the center
        :param width: Width of the mirror
        :param height: Height of the mirror
        """

        # Set the default width of the mirror
        self.width = width

        # Set the default height of the mirror
        self.height = height

        # Set the rotation angle of the mirror
        self.rotation = 0

        # Set the position of the mirror
        self.pos = Point(x, y)

        # Set the material of the mirror with default transparency and refractive index
        self.material = Material(100, 10000)

        # Initialize the list of equations for the mirror's sides
        self.eqs = []
        self.calcEqs()

        # Initialize the list of coordinates for the mirror's vertices
        self.coords = []
        self.calcCoords()

        # Assign a unique ID to the mirror and add it to the list of mirrors in the OpticsSolver
        self.id = OpticsSolver.getNextID()
        Solver.optical_objects.append(self)

    def get_collisions(self, ray):
        pass

    def calcCoords(self):
        """
        Calculates and updates the coordinates of the vertices.
        """
        return
        self.coords = [
            sp.solve((self.getLeftEq(), self.getBtmEq()), (Figure.x, Figure.y)),
            sp.solve((self.getLeftEq(), self.getTopEq()), (Figure.x, Figure.y)),
            sp.solve((self.getRightEq(), self.getTopEq()), (Figure.x, Figure.y)),
            sp.solve((self.getRightEq(), self.getBtmEq()), (Figure.x, Figure.y))
        ]

        for i in range(len(self.coords)):
            self.coords[i] = Point(self.coords[i][Figure.x], self.coords[i][Figure.y])

    def calcEqs(self):
        """
        Calculates and updates the equations of the sides.
        """
        self.eqs = [
            self.getLeftEq(),
            self.getRightEq(),
            self.getTopEq(),
            self.getBtmEq()
        ]

    def getRightEq(self):
        """
        Returns the equation of the right side.

        :return: Equation of the right side
        :rtype: sympy.Eq
        """
        moveX = self.width / 2 * sp.sin(self.rotation)
        moveY = self.width / 2 * sp.cos(self.rotation)

        x = self.pos.x + moveX
        y = self.pos.y - moveY

        return Straight.getStraightAtPointWithAngle(x, y, self.rotation).eq

    def getLeftEq(self):
        """
        Returns the equation of the left side.

        :return: Equation of the left side
        :rtype: sympy.Eq
        """
        moveX = self.width / 2 * sp.sin(self.rotation)
        moveY = self.width / 2 * sp.cos(self.rotation)

        x = self.pos.x - moveX
        y = self.pos.y + moveY

        return Straight.getStraightAtPointWithAngle(x, y, self.rotation).eq

    def getBtmEq(self):
        """
        Returns the equation of the bottom side.

        :return: Equation of the bottom side
        :rtype: sympy.Eq
        """
        moveX = self.height / 2 * sp.cos(self.rotation)
        moveY = self.height / 2 * sp.sin(self.rotation)

        x = self.pos.x - moveX
        y = self.pos.y - moveY

        return Straight.getStraightAtPointWithAngle(x, y, 90 + self.rotation).eq

    def getTopEq(self):
        """
        Returns the equation of the top side.

        :return: Equation of the top side
        :rtype: sympy.Eq
        """
        moveX = self.height / 2 * sp.cos(self.rotation)
        moveY = self.height / 2 * sp.sin(self.rotation)

        x = self.pos.x + moveX
        y = self.pos.y + moveY

        return Straight.getStraightAtPointWithAngle(x, y, 90 + self.rotation).eq

    def getRayTangentEqAndPoint(self, ray):
        """
        Returns a list with the point and the equation of the line
        on which the ray falls.

        :param ray: The ray
        :type ray: Ray

        :return: List with the equation of the line and the collision point
        :rtype: list[sympy.Eq, Point]
        """

        # Punkt kolizji lasera z lustrem
        mirrorTangent = None

        # Równanie prostej, która koliduje z promieniem
        mirrorTangentEq = None

        for i in range(len(self.eqs)):
            mEq = self.eqs[i]

            tangents = ray.getTangentPointsWithEq(mEq)

            if not tangents:
                continue

            for tangent in tangents:
                if not (
                        tangent.isOnStretch(self.coords[0], self.coords[1]) or
                        tangent.isOnStretch(self.coords[2], self.coords[3]) or
                        tangent.isOnStretch(self.coords[1], self.coords[2]) or
                        tangent.isOnStretch(self.coords[0], self.coords[3])
                ):
                    continue

                if mirrorTangent:
                    if tangent.getDistance(ray.getStartPoint()) < mirrorTangent.getDistance(ray.getStartPoint()):
                        mirrorTangent = tangent
                        mirrorTangentEq = mEq
                else:
                    mirrorTangent = tangent
                    mirrorTangentEq = mEq

        return [mirrorTangentEq, mirrorTangent]
