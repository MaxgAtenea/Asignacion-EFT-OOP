import pandas as pd
from . import constants
from .constants import RECURSOS_POR_RUTA

from .base import AsignacionBase

class AsignacionNuevosAntiguos(AsignacionBase):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase con los métodos para gestionar la asignación de recursos para la ruta 'Antiguos' o 'Nuevos'.
    """
    
    def __init__(self, data, nombre_ruta):
        """
        TO DO: Descripcion

        Parameters:
        - data (pandas dataframe): Dataframe con la inforamcion de los programas Antiguos
        - nombre_ruta: el nombre de la ruta como se especifica en las llaves de constants.RECURSOS_POR_RUTA
        """
        
        super().__init__(RECURSOS_POR_RUTA[nombre_ruta])
        self.data = data
        self.recursosxcno = pd.DataFrame()
        self.nombre_ruta = nombre_ruta

        self.calcular_recursos_por_cno()
        
    def _ponderar_ipo(self, alfa = 1, ponderar = True):
        """
        Calcula el IPO ponderado como (ipo^alfa) * cupos, si `ponderar` es True.
        De lo contrario no pondera el IPO. 
    
        Parámetros:
        - alfa (float): Exponente aplicado al ipo (≥ 1).
        - ponderar (bool): Si False, no se pondera por cupos.
    
        Crea la columna 'ipo_ponderado' en el DataFrame self.data.
        """
    
        # Validación del parámetro alfa
        if not isinstance(alfa, (int, float)):
            raise TypeError("El parámetro 'alfa' debe ser un número.")
        if alfa < 1:
            raise ValueError("El parámetro 'alfa' debe ser mayor o igual a 1.")
        
        if ponderar:
            self.data['ipo_ponderado'] = self.data['numero_cupos_ofertar'] * (self.data['ipo'] ** alfa)
        else:
            alfa = 1
            beta = 0
            self.data['ipo_ponderado'] = (self.data['numero_cupos_ofertar']**beta) * (self.data['ipo'] ** alfa)


    def calcular_recursos_por_cno(self, alfa=1, ponderar=True, group=['cod_CNO']):
        """
        Calcula y distribuye recursos por grupo ocupacional (CNO) en función del ipo ponderado.
    
        Aplica una ponderación al ipo, agrupa los datos por las columnas especificadas en `group`,
        calcula la participación relativa de cada grupo en el total ponderado y asigna recursos
        proporcionalmente. Adjunta los resultados al dataframe self.data.
    
        Parámetros:
        ----------
        alfa : float, opcional (default=1)
            Exponente para ponderar el ipo. Debe ser ≥ 1.
        ponderar : bool, opcional (default=True)
            Indica si se pondera el ipo por número de cupos ofertados.
        group : list[str], opcional (default=['cod_CNO'])
            Columnas por las que se agrupan los datos.
    
        Retorna:
        -------
        pd.DataFrame
            DataFrame con recursos asignados por grupo, incluyendo columnas: 'recursosxcno',
            y 'n_programas'.
        """
        self._ponderar_ipo(alfa=alfa, ponderar=ponderar)
    
        # Calcular total de ipo ponderado
        ipo_ponderado_total = self.data['ipo_ponderado'].sum()
    
        # Agrupar datos por CNO y calcular métricas
        grouped = (
            self.data
            .groupby(group)
            .agg(
                ipo_ponderado=('ipo_ponderado', 'sum'),
                cuposxcno=('numero_cupos_ofertar', 'sum'),
                ipo=('ipo', 'sum'),
                n_programas=('ipo_ponderado', 'count')
            )
            .reset_index()
        )
    
        # Calcular participación relativa y asignar recursos
        grouped['participacion_ipo'] = grouped['ipo_ponderado'] / ipo_ponderado_total
        grouped['recursosxcno'] = grouped['participacion_ipo'] * self.recursos_disponibles
        
        self.recursosxcno = grouped
        
        # Agregar columna de recursos al DataFrame original
        self.data = self.data.merge(
            grouped[group + ['recursosxcno']],
            on=group,
            how='left'
        )

        return grouped

    def exportar_recursos_por_cno(self):
        """
        Exporta el resultado de los recursos asignados por cno
        """
        ruta =  "../" + self.path_export + self._subdirectorio_resultados + "recursosxcno_" + self.nombre_ruta + ".xlsx"
        print(f"Guardado en: {ruta}")
        self.recursosxcno.to_excel(ruta , index=False)

        