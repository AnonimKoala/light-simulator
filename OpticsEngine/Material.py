class Material:
    """
    The `Material` class allows the creation of materials with unique properties.
    """

    def __init__(self, transparency, fracture):
        """
        Initializes an instance of the `Material` class.

        :param transparency: Transparency of the material
        :type transparency: float

        :param fracture: Refractive index of the material
        :type fracture: float
        """
        self.transparency = transparency
        self.fracture = fracture

    def setTransparency(self, t):
        """
        Sets the transparency of the material.

        :param t: Transparency
        :type t: float
        """
        self.transparency = t

    def setFracture(self, f):
        """
        Sets the refractive index of the material.

        :param f: Refractive index
        :type f: float
        """
        self.fracture = f

    @staticmethod
    def glass():
        """
        Returns a material with the properties of glass.

        - Transparency: 100%
        - Refractive index: 1.5

        :return: Material
        :rtype: Material
        """
        return Material(100, 1.5)
