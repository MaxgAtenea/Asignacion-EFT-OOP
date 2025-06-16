import pandas as pd
from . import constants
from .base import AsignacionBase

class AsignacionCerrados(AsignacionBase):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Cerrados'.
    """

    def __init__(self, data):
        super().__init__(RECURSOS_POR_RUTA["cerrados"])
        self.data = data

    def preparar_datos_cerrados(self):
        """
        Aplica reglas y filtros específicos para programas cerrados.
        """
        pass

    def asignar_recursos_cerrados(self):
        """
        Implementa la lógica de asignación de recursos específica para la ruta 'Cerrados'.
        """
        pass