import pandas as pd
from . import constants

from .nuevosyantiguos import AsignacionNuevosAntiguos

class AsignacionNuevos(AsignacionNuevosAntiguos):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Viejos'.
    """

    def __init__(self, data):
        super().__init__(RECURSOS_POR_RUTA["nuevos"])
        self.data = data

    def preparar_datos_nuevos(self):
        """
        Aplica reglas y filtros específicos para programas 'Viejos'.
        """
        pass

    def asignar_recursos_nuevos(self):
        """
        Implementa la lógica de asignación de recursos específica para la ruta 'Viejos'.
        """
        pass

    def ordenar_ocupaciones_por_puntaje(self):
        """
        TODO: Definir funcion
        """
        pass