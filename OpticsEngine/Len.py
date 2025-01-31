from Geometry import Circle, Point
from Material import Material
from OpticsSolver import OpticsSolver


class Len:
    """
    The class allows creating lenses.
    """

    # Domyślna grubość
    INIT_DIAMETER = 10

    # Domyślny promień wewnętrzny soczewki
    INIT_INNER_RADIUS = INIT_DIAMETER / 2

    # Domyślna krzywizna
    INIT_CURVATURE = 5

    def __init__(self, x, y):
        """
        Initializes an instance of the `Len` class.

        :param x: X-coordinate of the lens
        :type x: float

        :param y: Y-coordinate of the lens
        :type y: float
        """

        # Set the position of the lens
        self.pos = Point(x, y)

        # Set the default diameter of the lens
        self.d = Len.INIT_DIAMETER

        # Set the left and right curvature radii of the lens
        self.lRadius = Len.INIT_CURVATURE
        self.rRadius = Len.INIT_CURVATURE

        # Set the left and right inner radii of the lens
        self.lInner = Len.INIT_INNER_RADIUS
        self.rInner = Len.INIT_INNER_RADIUS

        # Set the material of the lens to glass
        self.material = Material.glass()

        # Initialize the equations for the left and right circles of the lens
        self.lEq = None
        self.rEq = None
        self.calcEqs()

        # Get a identifier for the lens and add it to the OpticsSolver's lens list
        self.uid = OpticsSolver.getNextID()
        OpticsSolver.LENS.append(self)

    def calcEqs(self):
        """
        Calculates and updates the equations of the circles
        that form the lens.
        """
        self.lEq = Circle(
            self.pos.x - self.lRadius + self.lInner,
            self.pos.y,
            self.lRadius
        )

        self.rEq = Circle(
            self.pos.x + self.rRadius - self.rInner,
            self.pos.y,
            self.rRadius
        )

    def scale(self, scale):
        """
        Scales the dimensions of the lens.

        :param scale: Target scale
        :type scale: float
        """
        self.d *= scale
        self.lInner = self.d / 2
        self.rInner = self.d / 2

        self.calcEqs()

    def setPos(self, x, y):
        """
        Moves the lens and updates its equations.

        :param x: X-coordinate
        :type x: float

        :param y: Y-coordinate
        :type y: float
        """
        self.pos = Point(x, y)
        self.calcEqs()

    def setD(self, d):
        """
        Sets the thickness of the lens and scales its dimensions.

        :param d: New thickness
        :type d: float
        """
        self.scale(d / self.d)

    def setLRadius(self, r):
        """
        Sets the left curvature radius and updates the lens equations.

        :param r: Left curvature radius
        :type r: float
        """
        self.lRadius = r
        self.calcEqs()

    def setRRadius(self, r):
        """
        Sets the right curvature radius and updates the lens equations.

        :param r: Right curvature radius
        :type r: float
        """
        self.rRadius = r
        self.calcEqs()

    def setLInner(self, inner):
        """
        Sets the distance from the center to the left edge of the lens,
        scaling its dimensions.

        :param inner: Distance
        :type inner: float
        """
        self.scale(inner / self.lInner)

    def setRInner(self, inner):
        """
        Sets the distance from the center to the right edge of the lens,
        scaling its dimensions.

        :param inner: Distance
        :type inner: float
        """
        self.scale(inner / self.rInner)
