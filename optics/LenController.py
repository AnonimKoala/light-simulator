from sympy import Point2D, cos, sin, pi, Ellipse, tan, Ray2D, Segment2D, Circle, Add, Eq
from sympy.abc import x, y

from conf import LEN_NORMAL_POINTS_DISTANCE
from optics.BasicController import BasicController
from optics.Material import Material
from optics.RayController import RayController
from optics.Solver import Solver
from optics.util import round_point, round_line, round_ray, round_segment, deg2rad, string_points, \
    is_point_inside_polygon


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

        self._pos = Point2D(pos_x, pos_y)
        self._height = height
        self._rotation = 0  # Rotation in radians about the OX axis
        self._left_radius = left_radius
        self._right_radius = right_radius
        self._d = d  # The thickness of the len
        self.material = Material.glass()

        self._vertices = {}
        self._sides = None
        self._curve_vertices = {}
        self._right_curve = None
        self._left_curve = None

        self.validate()
        self.update_props()
        Solver.optical_objects.append(self)

    def validate(self):
        """
        Validates the properties of the lens.
        Raises ValueError if any property is invalid.
        """
        if self.d < self.left_radius + self.right_radius:
            raise ValueError("The thickness of the lens must be greater than the sum of the radii.")
        if self.d < 0:
            raise ValueError("The thickness of the lens must be a positive value.")
        if self.height <= 0:
            raise ValueError("The height of the lens must be a positive value.")

    def get_collision(self, ray: Ray2D) -> dict[str, Point2D | Segment2D | bool] | None:
        intersections = []
        has_collision = False
        for key, side in self.sides.items():
            if Solver.first_intersection(ray, side):
                has_collision = True
        if not has_collision:
            return None

        def check_curve(ray_obj: Ray2D, curve_eq: Eq, h_radius: float, side_type: str):
            if not (curve_intersections := Solver.all_intersections(ray_obj, curve_eq)):
                return None
            curve_intersections = Solver.sort_by_distance(ray_obj.source, curve_intersections)
            print("Curve intersections:", string_points(curve_intersections))
            polygon = []
            if h_radius >= 0:
                polygon = [
                    self.vertices[f"top-{side_type}"],
                    self.vertices[f"bottom-{side_type}"],
                    self.curve_vertices[f"{side_type}-bottom"],
                    self.curve_vertices[f"{side_type}-top"]
                ]
            elif h_radius < 0:
                polygon = [
                    self.vertices[f"top-left"],
                    self.vertices[f"bottom-left"],
                    self.vertices[f"bottom-right"],
                    self.vertices[f"top-right"],
                ]
            for point in curve_intersections:
                if is_point_inside_polygon(point, polygon):
                    print(f"is_point_inside {side_type} : {string_points(point)}")
                    circle_x, circle_y = point
                    circle_eq = Eq((x - circle_x) ** 2 + (y - circle_y) ** 2, LEN_NORMAL_POINTS_DISTANCE ** 2)
                    return {
                        "point": point,
                        "side": Segment2D(
                            *Solver.solve_safe(curve_eq, circle_eq)
                        )
                    }
            return None

        for curve, radius, side in [(self.left_curve, self.left_radius, "left"), (self.right_curve, self.right_radius, "right")]:
            intersection = check_curve(ray, curve, radius, side)
            if intersection:
                intersections.append(intersection)
        intersections = list(filter(lambda cp: cp["point"] != round_point(ray.source), intersections))
        if intersections:
            print("Intersections found:", intersections)
            closest_intersection = min(intersections, key=lambda cp: cp["point"].distance(ray.source))
            print("got intersection:", string_points(closest_intersection))
            print("With ray:", ray)
            return {
                "surface": closest_intersection["side"],
                "point": closest_intersection["point"],
                "normal": round_line(closest_intersection["side"].perpendicular_line(closest_intersection["point"])),
                "material": self.material,
                "is-from-inside": self.is_point_inside(ray.source),
                "thickness": self.d/100  # Assuming thickness [m] is the width of the lens
            }
        return None


    def is_point_inside(self, point: Point2D) -> bool:
        """
        Checks if a point is inside the lens's area.

        Warning:
           This function is in **beta**.
           It does not give reliable results for all cases.

        :param point: The point to check
        :type point: Point2D
        :return: True if the point is inside, False otherwise
        """
        polygon = [
            self.vertices["top-left"],
            self.vertices["top-right"],
            self.vertices["bottom-right"],
            self.vertices["bottom-left"]
        ]
        return is_point_inside_polygon(point, polygon)

    def update_props(self):
        """
        Calculates and updates the len.
        """
        self.calc_curve_vertices()
        self.calc_vertices()
        self.calc_sides()
        self.calc_left_curve()
        self.calc_right_curve()
        # todo check if the equation is correct, the rotation is correct

    @property
    def vertices(self) -> dict:
        return self._vertices

    def calc_vertices(self):
        height2cos = (self.height / 2) * cos(deg2rad(self.rotation))
        height2sin = (self.height / 2) * sin(deg2rad(self.rotation))
        restd2 = (self.d - abs(self.left_radius) - abs(self.right_radius)) / 2

        d2cos_left = (abs(self.left_radius) + restd2)  * cos(deg2rad(self.rotation))
        d2sin_left = (abs(self.left_radius) + restd2) * sin(deg2rad(self.rotation))
        d2cos_right = (abs(self.right_radius) + restd2) * cos(deg2rad(self.rotation))
        d2sin_right = (abs(self.right_radius) + restd2) * sin(deg2rad(self.rotation))

        self._vertices = {
            "top-left": round_point(Point2D(self.pos.x - d2cos_left - height2sin, self.pos.y - d2sin_left + height2cos)),
            "top-right": round_point(Point2D(self.pos.x + d2cos_right - height2sin, self.pos.y + d2sin_right + height2cos)),
            "bottom-right": round_point(Point2D(self.pos.x + d2cos_right + height2sin, self.pos.y + d2sin_right - height2cos)),
            "bottom-left": round_point(Point2D(self.pos.x - d2cos_left + height2sin, self.pos.y - d2sin_left - height2cos)),
        }

        print("Vertices:", self._vertices)

    @property
    def sides(self) -> dict:
        return self._sides

    def calc_sides(self):
        self._sides = {
            "top": Segment2D(self.vertices["top-left"], self.vertices["top-right"]),
            "bottom": Segment2D(self.vertices["bottom-left"], self.vertices["bottom-right"]),
            "left": Segment2D(self.vertices["top-left"], self.vertices["bottom-left"]),
            "right": Segment2D(self.vertices["top-right"], self.vertices["bottom-right"]),
        }

    @property
    def curve_vertices(self) -> dict:
        return self._curve_vertices

    def calc_curve_vertices(self):
        h2sin = (self.height / 2) * sin(self.rotation)
        h2cos = (self.height / 2) * cos(self.rotation)
        rest_d2 = (self.d - abs(self.left_radius) - abs(self.right_radius)) / 2

        left_shift = abs(self.left_radius) + rest_d2 if self.left_radius < 0 else rest_d2
        d2rest_cos_left = left_shift * cos(self.rotation)
        d2rest_sin_left = left_shift * sin(self.rotation)

        right_shift = abs(self.right_radius) + rest_d2 if self.right_radius < 0 else rest_d2
        d2rest_cos_right = right_shift * cos(self.rotation)
        d2rest_sin_right = right_shift * sin(self.rotation)

        result = {  # Stores middle top/bottom points of curves
            "left-top": Point2D(
                self.pos.x - d2rest_cos_left - h2sin,
                self.pos.y - d2rest_sin_left + h2cos),
            "left-bottom": Point2D(self.pos.x - d2rest_cos_left + h2sin, self.pos.y - d2rest_sin_left - h2cos),
            "right-top": Point2D(self.pos.x + d2rest_cos_right - h2sin, self.pos.y + d2rest_sin_right + h2cos),
            "right-bottom": Point2D(self.pos.x + d2rest_cos_right + h2sin, self.pos.y + d2rest_sin_right - h2cos),
        }
        for key, point in result.items():
            result[key] = round_point(point)
        print(result)
        self._curve_vertices = result

        print("Curve vertices:", self._curve_vertices)

    @property
    def left_curve(self):
        return self._left_curve

    def calc_left_curve(self):
        pos_x, pos_y = self.curve_vertices["left-top"].midpoint(self.curve_vertices["left-bottom"])
        h_radius = abs(self.left_radius)
        v_radius = self.curve_vertices["left-top"].distance(self.curve_vertices["left-bottom"])
        theta = tan(self.rotation)
        print(f"Left curve: pos=({pos_x}, {pos_y}), h_radius={h_radius}, v_radius={v_radius}, theta={theta}")
        self._left_curve = Solver.calc_ellipse_eq(pos_x, pos_y, h_radius, v_radius, theta)

    @property
    def right_curve(self):
        return self._right_curve

    def calc_right_curve(self):
        pos_x, pos_y = self.curve_vertices["right-top"].midpoint(self.curve_vertices["right-bottom"])
        h_radius = abs(self.right_radius)
        v_radius = self.curve_vertices["right-top"].distance(self.curve_vertices["right-bottom"])
        theta = tan(self.rotation)
        print(f"Right curve: pos=({pos_x}, {pos_y}), h_radius={h_radius}, v_radius={v_radius}, theta={theta}")
        self._right_curve = Solver.calc_ellipse_eq(pos_x, pos_y, h_radius, v_radius, theta)

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
