from sympy import Point2D, cos, sin, pi, Ellipse, tan, Ray2D, Segment2D, Circle, Add, Eq
from sympy.abc import x, y

from conf import LEN_NORMAL_POINTS_DISTANCE
from optics.BasicController import BasicController
from optics.RayController import RayController
from optics.Solver import Solver
from optics.util import round_point, round_line, round_ray, round_segment, deg2rad


class LenController(BasicController):
    """
    The class allows creating lenses.
    """

    DEFAULT_RADIUS = 20
    DEFAULT_HEIGHT = 100

    def __init__(self, pos_x, pos_y, d, height=DEFAULT_HEIGHT, left_radius=DEFAULT_RADIUS, right_radius=DEFAULT_RADIUS):
        """
        Initializes an instance of the `Len` class.

        :param pos_x: X-coordinate of the lens
        :type pos_x: float

        :param pos_y: Y-coordinate of the lens
        :type pos_y: float
        """

        self.pos = Point2D(pos_x, pos_y)
        self.height = height
        self.rotation = 0  # Rotation in radians about the OX axis
        self.left_radius = left_radius
        self.right_radius = right_radius
        self.d = d  # The thickness of the len

        self.update_props()
        Solver.optical_objects.append(self)

    def get_collision(self, ray: Ray2D) -> dict[str, Point2D | Segment2D] | None:
        intersections = []
        has_collision = False
        for key, side in self.sides.items():
            if Solver.first_intersection(ray, side):
                has_collision = True
        if not has_collision:
            return None

        def check_curve(ray_obj: Ray2D, curve_eq: Eq, h_radius: float):
            if not (curve_intersections := Solver.all_intersections(ray_obj, curve_eq)):
                return None
            curve_intersections = Solver.sort_by_distance(ray_obj.source, curve_intersections)
            print("Curve intersections:", curve_intersections)
            if h_radius >= 0:
                circle_x, circle_y = curve_intersections[0]
                circle_eq = Eq((x - circle_x) ** 2 + (y - circle_y) ** 2, LEN_NORMAL_POINTS_DISTANCE ** 2)
                return {
                    "point": curve_intersections[0],
                    "side": Segment2D(
                        *Solver.solve_safe(curve_eq, circle_eq)
                    )
                }
            elif h_radius < 0:
                circle_x, circle_y = curve_intersections[-1]
                circle_eq = Eq((x - circle_x) ** 2 + (y - circle_y) ** 2, LEN_NORMAL_POINTS_DISTANCE ** 2)
                return {
                    "point": curve_intersections[-1],
                    "side": Segment2D(
                        *Solver.solve_safe(curve_eq, circle_eq)
                    )
                }
            return None

        for curve, radius in [(self.left_curve, self.left_radius), (self.right_curve, self.right_radius)]:
            intersection = check_curve(ray, curve, radius)
            print("curve", curve)
            if intersection:
                intersections.append(intersection)
        intersections = list(filter(lambda cp: cp["point"] != round_point(ray.source), intersections))
        if intersections:
            closest_intersection = min(intersections, key=lambda cp: cp["point"].distance(ray.source))
            return {
                "surface": closest_intersection["side"],
                "point": closest_intersection["point"],
                "normal": round_line(closest_intersection["side"].perpendicular_line(closest_intersection["point"])),
            }
        return None

    def update_props(self):
        """
        Calculates and updates the len.
        """

        # todo check if the equation is correct, the rotation is correct
        # todo Update the equations of the sides

    @property
    def vertices(self) -> dict:
        d2cos = (self.d / 2) * cos(deg2rad(self.rotation))
        d2sin = (self.d / 2) * sin(deg2rad(self.rotation))
        height2cos = (self.height / 2) * cos(deg2rad(self.rotation))
        height2sin = (self.height / 2) * sin(deg2rad(self.rotation))

        return {
            "top-left": round_point(Point2D(self.pos.x - d2cos - height2sin, self.pos.y - d2sin + height2cos)),
            "top-right": round_point(Point2D(self.pos.x + d2cos - height2sin, self.pos.y + d2sin + height2cos)),
            "bottom-right": round_point(Point2D(self.pos.x + d2cos + height2sin, self.pos.y + d2sin - height2cos)),
            "bottom-left": round_point(Point2D(self.pos.x - d2cos + height2sin, self.pos.y - d2sin - height2cos)),
        }

    @property
    def sides(self) -> dict:
        return {
            "top": Segment2D(self.vertices["top-left"], self.vertices["top-right"]),
            "bottom": Segment2D(self.vertices["bottom-left"], self.vertices["bottom-right"]),
            "left": Segment2D(self.vertices["top-left"], self.vertices["bottom-left"]),
            "right": Segment2D(self.vertices["top-right"], self.vertices["bottom-right"]),
        }

    @property
    def curve_vertices(self) -> dict:
        h2sin = (self.height / 2) * sin(self.rotation)
        h2cos = (self.height / 2) * cos(self.rotation)
        rest_d2 = (self.d - self.left_radius - self.right_radius) / 2
        d2rest_cos = (self.d / 2 + rest_d2) * cos(self.rotation)
        d2rest_sin = (self.d / 2 + rest_d2) * sin(self.rotation)

        return {  # Stores middle top/bottom points of curves
            "left-top": Point2D(self.pos.x - d2rest_cos - h2sin, self.pos.y - d2rest_sin + h2cos),
            "left-bottom": Point2D(self.pos.x - d2rest_cos + h2sin, self.pos.y - d2rest_sin - h2cos),
            "right-top": Point2D(self.pos.x + d2rest_cos - h2sin, self.pos.y + d2rest_sin + h2cos),
            "right-bottom": Point2D(self.pos.x + d2rest_cos + h2sin, self.pos.y + d2rest_sin - h2cos),
        }

    @property
    def left_curve(self):
        pos_x, pos_y = self.curve_vertices["left-top"].midpoint(self.curve_vertices["left-bottom"])
        h_radius = abs(self.left_radius)
        v_radius = self.curve_vertices["left-top"].distance(self.curve_vertices["left-bottom"])
        theta = tan(self.rotation)

        return Solver.calc_ellipse_eq(pos_x, pos_y, h_radius, v_radius, theta)

    @property
    def right_curve(self):
        pos_x, pos_y = self.curve_vertices["right-top"].midpoint(self.curve_vertices["right-bottom"])
        h_radius = abs(self.right_radius)
        v_radius = self.curve_vertices["right-top"].distance(self.curve_vertices["right-bottom"])
        theta = tan(self.rotation)
        return Solver.calc_ellipse_eq(pos_x, pos_y, h_radius, v_radius, theta)

    def scale(self, scale_factor: float):
        """
        Scales the dimensions of the len.
        """
        self.d *= scale_factor
        self.height *= scale_factor
        self.left_radius *= scale_factor
        self.right_radius *= scale_factor
        self.update_props()

    @property
    def pos(self) -> Point2D:
        return self._pos

    @pos.setter
    def pos(self, point: Point2D):
        self._pos = point
        self.update_props()

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float):
        self._height = height
        self.update_props()

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: float):
        self._rotation = rotation
        self.update_props()

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
        self.update_props()

    @property
    def left_radius(self) -> float:
        return self._left_radius

    @left_radius.setter
    def left_radius(self, radius: float):
        self._left_radius = radius
        self.update_props()

    @property
    def right_radius(self) -> float:
        return self._right_radius

    @right_radius.setter
    def right_radius(self, radius: float):
        self._right_radius = radius
        self.update_props()
