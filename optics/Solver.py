from math import exp
from sympy import Point2D, Segment2D, Line2D, Ray, Ray2D, pi, cos, sin, solve, Eq, tan, asin
from sympy.abc import x, y
from sympy.geometry.entity import GeometrySet
from conf import RAY_MAX_LENGTH, MAX_REFRACTIONS
from optics.BasicController import BasicController
from optics.util import round_point, round_ray, angle_to_ox, string_points


class Solver:
    optical_objects: list[BasicController] = []
    lasers = []
    OX = Line2D(Point2D(0, 0), Point2D(1, 0))

    @staticmethod
    def find_first_collision(ray: Ray2D) -> dict[str, Point2D | Segment2D] | None:
        """
        Detects the collision of a ray with optical objects.
        :param ray: The ray to check for collisions
        :type ray: Ray
        """
        print("first_collision called with ray:", ray)
        collisions = []
        for obj in Solver.optical_objects:
            if collision_data := obj.get_collision(ray):
                collisions.append(collision_data)
        if collisions:
            # Filter out collisions that are the same as the ray source
            collisions = [cp for cp in collisions if round_point(cp["point"]) != round_point(ray.source)]
            if not collisions:
                print("No collisions found for ray:", ray)
                return None
            nearest = min(collisions, key=lambda cp: cp["point"].distance(round_point(ray.source)))
            nearest["point"] = round_point(nearest["point"])
            return nearest
        return None

    @staticmethod
    def nearest_to_origin(origin, objs):
        """
        Finds the nearest object to the origin.
        :param origin: The origin point
        :type origin: Point2D
        :param objs: List of objects to check
        :type objs: list[Point2D]
        :return: The nearest object to the origin
        """
        return min(objs, key=lambda obj: obj.distance(origin))

    @staticmethod
    def sort_by_distance(origin, objs):
        """
        Sorts objects by their distance to the origin.
        :param origin: The origin point
        :type origin: Point2D
        :param objs: List of objects to check
        :type objs: list[Point2D]
        :return: List of objects sorted by distance to the origin
        """
        return sorted(objs, key=lambda obj: obj.distance(origin))

    @staticmethod
    def get_path(ray: Ray2D) -> list[dict[str, Point2D]]:
        collisions = []

        def compute_ray_reflection(incident_ray: Ray2D, collision_obj, alpha_primary) -> None | list:
            if not collision_obj:
                return None
            # Calculate the angle of incidence and reflection in radians
            normal_angle_to_ox = angle_to_ox(collision_obj['normal'])
            new_ray_angle_to_ox = 2 * normal_angle_to_ox - angle_to_ox(incident_ray) + pi
            # Moving the ray source point by vector to prevent it from being on the surface and causing infinite loop
            new_ray_source = round_point(
                collision_obj["point"] + Point2D(cos(new_ray_angle_to_ox), sin(new_ray_angle_to_ox)) * 2)
            new_ray = Ray2D(new_ray_source, angle=new_ray_angle_to_ox)
            # Determine the refractive indices based on whether the ray is entering or exiting the medium
            if collision_obj["is-from-inside"]:
                n1 = collision_obj["material"].refractive_index
                n2 = 1
            else:
                n1 = 1
                n2 = collision_obj["material"].refractive_index
            # Calculate the absorption coefficient
            alpha_color = Solver.calculate_alpha(alpha_primary, n1, n2, 0, 0, n2)
            return [round_ray(new_ray), alpha_color]

        def compute_ray_refraction(incident_ray: Ray2D, collision_obj, alpha_primary: float) -> None | list:
            if not collision_obj:
                return None
            # Calculate the angle of incidence and refraction in radians
            normal_angle_to_ox = angle_to_ox(collision_obj['normal'])
            ray_angle_to_ox = angle_to_ox(incident_ray)
            # Determine the refractive indices based on whether the ray is entering or exiting the medium
            if collision_obj["is-from-inside"]:
                n1 = collision_obj["material"].refractive_index
                n2 = 1
            else:
                n1 = 1
                n2 = collision_obj["material"].refractive_index
            # Calculate the absorption coefficient
            alpha_color = Solver.calculate_alpha(alpha_primary, n1, n2, collision_obj["material"].absorption_coefficient, collision_obj["thickness"])
            print(f"n1: {n1}, n2: {n2}, alpha_primary: {alpha_primary}, absorption_coefficient: {collision_obj['material'].absorption_coefficient}, thickness: {collision_obj['thickness']}")
            print("alpha_color:", alpha_color)
            # Using Snell's law to calculate the angle of refraction
            angle_of_incident = ray_angle_to_ox - normal_angle_to_ox
            sin_beta = (n1 / n2) * sin(angle_of_incident)
            if abs(sin_beta) > 1:
                print("Total internal reflection, returning None")
                return None
            # Calculate the angle of refraction
            beta_rad = asin(sin_beta)
            new_ray_angle_to_ox = normal_angle_to_ox + beta_rad
            # Calculate the new ray source point
            new_ray_source = round_point(
                collision_obj["point"] + Point2D(cos(new_ray_angle_to_ox), sin(new_ray_angle_to_ox)) * 2)
            new_ray = Ray2D(new_ray_source, angle=new_ray_angle_to_ox)
            return [round_ray(new_ray), alpha_color]
        rays_fifo = [[ray, 255]]
        i = 0
        while True:
            i += 1
            print(f"Iteration {i}, ray: {ray}")
            if len(rays_fifo) > 0:
                ray, alpha = rays_fifo.pop()
                if collision := Solver.find_first_collision(ray):
                    collisions.append({
                        "start": round_point(ray.source),
                        "end": round_point(collision["point"]),
                        "alpha_color": alpha
                    })
                    # if result := compute_ray_reflection(ray, collision, alpha):
                    #     rays_fifo.append(result)
                    if result := compute_ray_refraction(ray, collision, alpha):
                        rays_fifo.append(result)

                else:
                    collisions.append(
                        {"start": round_point(ray.source), "end": round_point(Solver.get_ray_inf_point(ray)), "alpha_color": alpha})
            else:
                break
            if i > MAX_REFRACTIONS:
                break
        return collisions

    @staticmethod
    def first_intersection(ray: Ray, obj) -> Point2D | None:
        if intersections := ray.intersection(obj):
            nearest = Solver.nearest_to_origin(round_point(ray.source), intersections)
            if isinstance(nearest, Segment2D):
                return round_point(Solver.nearest_to_origin(round_point(ray.source), [nearest.p1, nearest.p2]))
            return round_point(nearest)
        return None

    @staticmethod
    def all_intersections(ray: Ray, obj) -> list[Point2D]:
        print("obj: ", obj)
        if not isinstance(obj, GeometrySet):  # For Eq objects like Ellipse.equation()
            A, B, C = Line2D(*ray.points).coefficients
            line_eq = Eq(A * x + B * y + C, 0)
            print("Line equation:", line_eq)
            points = Solver.solve_safe(line_eq, obj)
            print("Solutions", string_points(points))
            return points

        if intersections := ray.intersection(obj):
            if any(not isinstance(i, Point2D) for i in intersections):
                raise NotImplementedError("all_intersections process only Point2D")
            return [round_point(i) for i in intersections]
        return []

    @staticmethod
    def get_ray_inf_point(ray: Ray2D) -> Point2D:
        ray_angle = angle_to_ox(ray)
        end_x = ray.source.x + RAY_MAX_LENGTH * cos(ray_angle)
        end_y = ray.source.y + RAY_MAX_LENGTH * sin(ray_angle)
        return round_point(Point2D(end_x, end_y))

    @staticmethod
    def solve_safe(obj1, obj2):
        """
        Solves the intersection of two objects, type similar, safely.
        :param obj1: The first object
        :param obj2: The second object
        :return: The intersection points or None if no intersection
        """
        solutions = solve([obj1, obj2], (x, y), dict=True)
        real_points = []
        for sol in solutions:
            x_val = list(sol.values())[0].evalf()
            y_val = list(sol.values())[1].evalf()
            if x_val.is_real and y_val.is_real:
                real_points.append(Point2D(x_val, y_val))
        return real_points

    @staticmethod
    def calc_ellipse_eq(pos_x: float, pos_y: float, h_radius: float, v_radius: float, theta: tan) -> Eq:
        """
        Calculates the equation of an ellipse.
        :param pos_x: X-coordinate of the ellipse center
        :param pos_y: Y-coordinate of the ellipse center
        :param h_radius: Horizontal radius of the ellipse
        :param v_radius: Vertical radius of the ellipse
        :param theta: Tangens of rotation angle in radians
        :return: The equation of the ellipse
        """
        if h_radius <= 0 or v_radius <= 0:
            raise ValueError("The radii of the lens must be positive values.")
        if theta == 0:
            return Eq((x - pos_x) ** 2 / (h_radius ** 2) + (y - pos_y) ** 2 / (v_radius ** 2), 1)
        return Eq(-1 + (-pos_y - theta * (-pos_x + x) + y) ** 2 / (v_radius ** 2 * (theta ** 2 + 1)) + (
                -pos_x + theta * (-pos_y + y) + x) ** 2 / (h_radius ** 2 * (theta ** 2 + 1)), 0)

    @staticmethod
    def calculate_alpha(alpha_initial: float, n1: float, n2: float, mu: float, thickness: float,
                        n_output: float = None) -> float:
        """
        Calculates the final alpha value after passing through a material layer.

        Parameters:
        :param alpha_initial: initial alpha channel value (0.0-1.0)
        :param n1: refractive index of the initial medium (e.g., air=1.0)
        :param n2: refractive index of the transparent medium (e.g., glass=1.5)
        :param mu: absorption coefficient [unit consistent with thickness]
            If you give it in cm⁻¹ (e.g. 0.1 cm⁻¹), then the thickness must be in centimeters
            If you give it in m⁻¹, then the thickness must be in meters
            (mu=0.1, thickness=15) is equivalent to (mu=10, thickness=0.15)
        :param thickness: material layer thickness
        :param n_output: refractive index of the output medium (default=n1)
        """
        if n_output is None:
            n_output = n1

        # Reflection coefficients calculation
        R_input = ((n2 - n1) / (n2 + n1)) ** 2
        R_output = ((n_output - n2) / (n_output + n2)) ** 2

        # Absorption calculation
        absorption = exp(-mu * thickness)

        # Full transmission model with multiple reflections
        numerator = (1 - R_input) * (1 - R_output) * absorption
        denominator = 1 - R_input * R_output * (absorption ** 2)

        total_transmission = numerator / denominator
        return alpha_initial * total_transmission
