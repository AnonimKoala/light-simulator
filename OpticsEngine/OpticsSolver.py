import sympy as sp
from .Ray import Ray


class OpticsSolver:
    """
    The `OpticsSolver` class provides methods for solving optical problems
    involving lasers, lenses, mirrors, and refracted rays.
    """

    # Identifier for each optical object.
    objID = 0

    # List to store all laser objects.
    LASERS = []

    # List to store all lens objects.
    LENS = []

    # List to store all mirror objects.
    MIRRORS = []

    # List to store all refracted ray objects.
    REFRACTED_RAYS = []

    @staticmethod
    def getNextID():
        """
        Returns the next unique object ID.

        :return: Next unique object ID
        :rtype: int
        """
        OpticsSolver.objID += 1
        return OpticsSolver.objID

    @staticmethod
    def calcRaysWayFromLaser():
        """
        Calculates the paths of rays emitted from lasers and updates their endpoints
        based on intersections with mirrors.
        """
        for laser in OpticsSolver.LASERS:
            for ray in laser.getRays():
                if not ray.getEndPoint():
                    for mirror in OpticsSolver.MIRRORS:
                        eq, point = mirror.getRayTangentEqAndPoint(ray)
                        ray.setEndPoint(point)

                        a = eq.lhs.coeff(sp.Symbol('x'))

                        rayRotation = (sp.atan(a) * (180 / sp.pi)).evalf()
                        newRotation = rayRotation - mirror.rotation
                        newRotation = 180 - newRotation + mirror.rotation

                        OpticsSolver.REFRACTED_RAYS.append(
                            Ray.getRayAtPointWithAngle(point, newRotation)
                        )



    @staticmethod
    def deleteObj(ID):
        """
        Deletes an object (laser, lens, or mirror) with the given unique ID.

        :param ID: Unique ID of the object to delete
        :type ID: int
        """
        for i in range(len(OpticsSolver.LENS)):
            if OpticsSolver.LENS[i].id == ID:
                OpticsSolver.LENS.pop(i)
                return

        for i in range(len(OpticsSolver.LASERS)):
            if OpticsSolver.LASERS[i].id == ID:
                OpticsSolver.LASERS.pop(i)
                return

        for i in range(len(OpticsSolver.MIRRORS)):
            if OpticsSolver.MIRRORS[i].id == ID:
                OpticsSolver.MIRRORS.pop(i)
                return

    @staticmethod
    def getConvexCollisionPoint(ray, circle_1, circle_2):
        """
        Returns the intersection point of a ray with the edge of a lens
        composed of two circles.

        :param ray: The ray
        :type ray: Ray

        :param circle_1: First circle
        :type circle_1: Circle

        :param circle_2: Second circle
        :type circle_2: Circle

        :return: Intersection point or None if no intersection exists
        :rtype: Point or None
        """
        pointsArr = [
            ray.getFigureTangentPoints(circle_1),
            ray.getFigureTangentPoints(circle_2)
        ]
        intersection = []  # Punkt przecięcia
        for p in pointsArr:
            for point in p:
                if ((point.getDistance(circle_1.centerPos) <= circle_1.r) and
                        (point.getDistance(circle_2.centerPos) <= circle_2.r)):
                    intersection.append(point)

        if not intersection:
            return None

        if intersection[0].getDistance(ray.getStartPoint()) < intersection[1].getDistance(ray.getStartPoint()):
            intersection.pop(1)
        else:
            intersection.pop(0)

        return intersection[0]
