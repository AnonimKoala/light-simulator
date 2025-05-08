from sympy import Point2D, cos, sin, pi, Ellipse, tan
from sympy.abc import x, y

from optics.BasicObject import BasicObject
from optics.RayController import RayController
from optics.Solver import Solver


class LenController(BasicObject):
    """
    The class allows creating lenses.
    """

    DEFAULT_RADIUS = 20
    DEFAULT_HEIGHT = 100

    def __init__(self, pos_x, pos_y, left_radius=DEFAULT_RADIUS, right_radius=DEFAULT_RADIUS):
        """
        Initializes an instance of the `Len` class.

        :param pos_x: X-coordinate of the lens
        :type pos_x: float

        :param pos_y: Y-coordinate of the lens
        :type pos_y: float
        """

        self._pos = Point2D(pos_x, pos_y)
        self._height = LenController.DEFAULT_HEIGHT
        self._rotation = pi / 2  # Rotation in radians about the OX axis
        self._d = abs(left_radius) + abs(right_radius)  # The thickness of the len
        self._left_radius = left_radius
        self._right_radius = right_radius

        self._left_curve_eq = None
        self._right_curve_eq = None
        self._vertices = {}  # Stores boundary points of the lens
        self._curve_vertices = {}  # Stores middle top/bottom points of curves

        self.calc()
        Solver.optical_objects.append(self)

    def get_collision(self, ray: RayController) -> Point2D:
        pass

    def calc(self):
        """
        Calculates and updates the len.
        """

        d2sin = (self.d / 2) * sin(self.rotation)
        d2cos = (self.d / 2) * cos(self.rotation)
        h2sin = (self.height / 2) * sin(self.rotation)
        h2cos = (self.height / 2) * cos(self.rotation)

        self._vertices: dict[str, Point2D] = {  # Stores the vertices of the len
            "top-left": Point2D(self.pos.x - d2cos - h2sin, self.pos.y - d2sin + h2cos),
            "top-right": Point2D(self.pos.x + d2cos - h2sin, self.pos.y + d2sin + h2cos),
            "bottom-left": Point2D(self.pos.x - d2cos + h2sin, self.pos.y - d2sin - h2cos),
            "bottom-right": Point2D(self.pos.x + d2cos + h2sin, self.pos.y + d2sin - h2cos),
        }

        rest_d2 = (self.d - self.left_radius - self.right_radius) / 2
        d2rest_cos = (self.d / 2 + rest_d2) * cos(self.rotation)
        d2rest_sin = (self.d / 2 + rest_d2) * sin(self.rotation)

        self._curve_vertices: dict[str, Point2D] = {  # Stores middle top/bottom points of curves
            "left-top": Point2D(self.pos.x - d2rest_cos - h2sin, self.pos.y - d2rest_sin + h2cos),
            "left-bottom": Point2D(self.pos.x - d2rest_cos + h2sin, self.pos.y - d2rest_sin - h2cos),
            "right-top": Point2D(self.pos.x + d2rest_cos - h2sin, self.pos.y + d2rest_sin + h2cos),
            "right-bottom": Point2D(self.pos.x + d2rest_cos + h2sin, self.pos.y + d2rest_sin - h2cos),
        }

        self._left_curve_eq = Ellipse(
            self._curve_vertices["left-top"].midpoint(self._curve_vertices["left-bottom"]),
            self._left_radius,
            self._curve_vertices["left-top"].distance(self._curve_vertices["left-bottom"])
        ).equation(x, y, _slope=tan(self.rotation))

        self._right_curve_eq = Ellipse(
            self._curve_vertices["right-top"].midpoint(self._curve_vertices["right-bottom"]),
            self._right_radius,
            self._curve_vertices["right-top"].distance(self._curve_vertices["right-bottom"])
        ).equation(x, y, _slope=tan(self.rotation))
        # todo check if the equation is correct, the rotation is correct
        # todo Update the equations of the sides

    def scale(self, scale_factor: float):
        """
        Scales the dimensions of the len.
        """
        self.d *= scale_factor
        self.height *= scale_factor
        self.left_radius *= scale_factor
        self.right_radius *= scale_factor
        self.calc()

    @property
    def pos(self) -> Point2D:
        return self._pos

    @pos.setter
    def pos(self, point: Point2D):
        self._pos = point
        self.calc()

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float):
        self._height = height
        self.calc()

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: float):
        self._rotation = rotation
        self.calc()

    @property
    def d(self) -> float:
        return self._d

    @d.setter
    def d(self, d: float):
        if d < self.left_radius + self.right_radius:
            raise ValueError("The thickness of the lens must be greater than the sum of the radii.")
        if d < 0:
            raise ValueError("The thickness of the lens must be a positive value.")
        self._d = d
        self.calc()

    @property
    def left_radius(self) -> float:
        return self._left_radius

    @left_radius.setter
    def left_radius(self, radius: float):
        self._left_radius = radius
        self.calc()

    @property
    def right_radius(self) -> float:
        return self._right_radius

    @right_radius.setter
    def right_radius(self, radius: float):
        self._right_radius = radius
        self.calc()

    @property
    def vertices(self) -> dict:
        return self._vertices

    @property
    def curve_vertices(self) -> dict:
        return self._curve_vertices
