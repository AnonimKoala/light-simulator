import sympy as sp


class Point:
    """
    The `Point` class allows the creation of coordinates and provides methods for operations on them.
    """

    def __init__(self, x, y):
        """
        Initializes an instance of the `Point` class.

        :param x: X-coordinate
        :type x: float

        :param y: Y-coordinate
        :type y: float
        """
        self.x = x
        self.y = y

    def __str__(self):
        """
        Returns a string representation of the point.

        :return: String representation of the point
        :rtype: str
        """
        return f"Point({self.x}, {self.y})"

    def getDistance(self, point):
        """
        Returns the distance between two points.

        :param point: The other point
        :type point: Point

        :return: Distance between the points
        :rtype: float
        """
        return sp.sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2)


    def isOnStretch(self, start_point, end_point):
        """
        Checks if the point lies on the straight between the given coordinates.

        :param start_point: Start point of the straight
        :type start_point: Point

        :param end_point: End point of the straight
        :type end_point: Point

        :return: True if the point lies on the straight, False otherwise
        :rtype: bool
        """
        subtraction = (self.getDistance(start_point) + self.getDistance(end_point)
                       - start_point.getDistance(end_point))

        # Checks if it meets the accuracy up to 0.001
        if not abs(subtraction) <= 0.001:
            return False

        return True


class Figure:
    """
    The `Figure` class serves as a parent class for geometric figures,
    providing methods related to their properties.
    """
    x, y = sp.symbols('x y')

    def __init__(self, a, b):
        """
        Initializes an instance of the `Figure` class.

        :param a: A component needed in geometry
        :param b: A component needed in geometry
        """
        self.a = a
        self.b = b
        self.eq = None

    def getTangentPointsWithEq(self, eq=None):
        """
        Returns the intersection points of the figure/line with another passed as a parameter.

        :param eq: The equation of the other figure/line (default is None)
        :type eq: sympy.Eq or None

        :return: A list of intersection points
        :rtype: list[Point]
        """
        if eq is None or self.eq is None:
            return []

        coords = sp.solve((self.eq, eq), (Figure.x, Figure.y))
        coordsArr = []
        for solution in coords:
            coordsArr.append(Point(solution[0].evalf(), solution[1].evalf()))

        return coordsArr

    def getFigureTangentPoints(self, figure=None):
        """
        Returns the intersection points of the figure/line with another passed as a parameter.

        :param figure: The other figure
        :type figure: Figure

        :return: A list of intersection points
        :rtype: list[Point]
        """
        return self.getTangentPointsWithEq(figure.eq)


class Circle(Figure):
    """
    The `Circle` class allows operations and creation of circles.
    """

    def __init__(self, a, b, r):
        """
        Initializes an instance of the `Circle` class.

        :param a: X-coordinate of the center
        :type a: float

        :param b: Y-coordinate of the center
        :type b: float

        :param r: Radius
        :type r: float
        """
        super().__init__(a, b)
        self.eq = sp.Eq((Figure.x - a) ** 2 + (Figure.y - b) ** 2, r ** 2)
        self.r = r
        self.centerPos = Point(a, b)


class Straight(Figure):
    """
    The `Straight` class allows operations and creation of straight lines.
    """

    def __init__(self, a, b):
        """
        Initializes an instance of the `Straight` class.

        :param a: Slope of the line
        :param b: Y-intercept of the line
        """

        super().__init__(a, b)
        self.eq = sp.Eq(Figure.y, a * Figure.x + b)

    def getLenContactPoint(self, circle_1, circle_2):
        """
        Returns the intersection points of the line with two circles.

        :param circle_1: The first circle
        :type circle_1: Circle

        :param circle_2: The second circle
        :type circle_2: Circle

        :return: A list of intersection points
        :rtype: list[Point]
        """

        pointsArr = [
            self.getFigureTangentPoints(circle_1),
            self.getFigureTangentPoints(circle_2)
        ]
        points = []

        intersection = []  # Punkt przecięcia
        for p in pointsArr:
            for point in p:

                if (point.getDistance(circle_1.centerPos) <= circle_1.r) and (
                        point.getDistance(circle_2.centerPos) <= circle_2.r):
                    intersection.append(point)

                    print(point)
                    points.append(point)

        return points

    @staticmethod
    def getStraightAtPointWithAngle(x, y, angle):
        a = sp.tan(angle * sp.pi / 180).evalf()
        b = y - (sp.tan(angle * sp.pi / 180).evalf() * x)
        return Straight(a, b)
