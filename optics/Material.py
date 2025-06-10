class Material:
    """
    The `Material` class allows the creation of materials with unique properties.
    """

    def __init__(self, transparency, refractive_index):
        """
        Initializes an instance of the `Material` class.

        :param transparency: Transparency of the material
        :type transparency: float

        :param refractive_index: Refractive index of the material
        :type refractive_index: float
        """
        self._transparency = transparency
        self._refractive_index = refractive_index

    @property
    def transparency(self):
        return self._transparency

    @transparency.setter
    def transparency(self, value):
        self._transparency = value

    @property
    def refractive_index(self):
        return self._refractive_index

    @refractive_index.setter
    def refractive_index(self, value):
        self._refractive_index = value

    @staticmethod
    def glass():
        """
        Returns a material with the properties of glass.

        - Transparency: 100%
        - Refractive index: 1.5
        """
        return Material(100, 1.5)
