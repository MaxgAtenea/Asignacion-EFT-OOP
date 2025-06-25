import pandas as pd
from . import constants
from .base import AsignacionBase

from .constants import RECURSOS_POR_RUTA
from .constants import COLUMNA_VALOR_PROGRAMA
from .constants import COLUMNA_CUPOS_MAXIMOS

class AsignacionCerrados(AsignacionBase):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Cerrados'.
    """

    def __init__(self, data):
        super().__init__(RECURSOS_POR_RUTA["cerrados"])
        self.data = data
        
        #Ordenamos programas siguiendo criterios (condición necesaria y previa para la asignacion de recursos)
        self._ordenar_programas()     
        
        #Garantiza que al instanciar la clase, se calcule la asignacion
        self.asignar_recursos()
        #Identificar los programas con cupos disponibles después de la asignacion
        self._identificar_programas_disponibles()

        
    def asignar_recursos(self):
        """
        TODO :  Completar documentación
        
        Asigna recursos a programas de grupos cerrados hasta agotar el saldo total disponible.
    
        Retorna:
            pd.DataFrame: DataFrame con columnas de cupos y recursos asignados, y el saldo restante.
        """
        data = self.data.copy()
        
        data['cupos_asignados_2E'] = 0  
        data['recurso_asignado_2E'] = 0.0
        data['saldo_total_remanente'] = 0.0
    
    
        saldo_total = self.recursos_iniciales
    
        for idx, row in data.iterrows():
            costo = row[COLUMNA_VALOR_PROGRAMA]
            cupos = min(row['numero_cupos_ofertar'], row[COLUMNA_CUPOS_MAXIMOS])
    
            if pd.isna(costo) or costo <= 0 or pd.isna(cupos) or cupos <= 0:
                data.at[idx, 'saldo_total_remanente'] = saldo_total
                continue
    
            recurso_necesario = costo * cupos
    
            if saldo_total >= recurso_necesario:
                data.at[idx, 'cupos_asignados_2E'] = cupos
                data.at[idx, 'recurso_asignado_2E'] = recurso_necesario
                saldo_total -= recurso_necesario
            else:
                
                cupos_posibles = saldo_total // costo
                recurso_asignado = cupos_posibles * costo
                
                data.at[idx, 'cupos_asignados_2E'] = cupos_posibles
                data.at[idx, 'recurso_asignado_2E'] = recurso_asignado
                saldo_total -= recurso_asignado
    
            data.at[idx, 'saldo_total_remanente'] = saldo_total
    
            if saldo_total <= 0:
                break

        self.recursos_disponibles = saldo_total 
        self.recursos_asignados = self.recursos_iniciales - self.recursos_disponibles

        self.asignacion = data

    def _ordenar_programas(self,usar_cod_cno=True):
        """
        Ordena los programas dentro del DataFrame según criterios establecidos.
        Si usar_cod_cno es True, cod_CNO se usará como primer criterio de orden.
        Actualiza self.data.
    
        Criterios de orden:
        1. (Opcional) cod_CNO
        2. Mayor puntaje
        3. Mayor número de cupos ofertados
        4. Mayor meta de vinculación
        5. Menor costo
        6. Menor duración
    .
    
        Retorna:
            pd.DataFrame: DataFrame ordenado según los criterios establecidos.
        """
        df = self.data.copy()
        
        columnas = []
        orden = []
    
        if usar_cod_cno:
            columnas.append('cod_CNO')
            orden.append(True)
    
        columnas += [
            'Puntaje (nuevos y cerrados)',
            'numero_cupos_ofertar',
            'Meta de vinculación',
            COLUMNA_VALOR_PROGRAMA,
            'duracion_horas_programa'
        ]
    
        orden += [False, False, False, True, True]
    
        self.data = df.sort_values(by=columnas, ascending=orden).reset_index(drop=True)

    def _identificar_programas_disponibles(self):
        """
        Identifica cuales programas después del la asignación quedaron con cupos disponibles.
        """        
        data = self.asignacion.copy()
        
        grupos_cerrados_remanente = data[
            data['numero_cupos_ofertar'] - data['cupos_asignados_2E'] > 0
        ].reset_index(drop=True)

        self.programas_disponibles = grupos_cerrados_remanente

    def asignar_remanente(self, bolsa):
        """
        TODO: completar definicion de la función.
        Asigna recursos a programas de grupos cerrados hasta agotar el saldo total disponible.
        TODO: Implementar función.
        Parametros:

        Retorna:
        """
        df_remanente =self.programas_disponibles.copy()
        self.bolsa_comun_disponible = bolsa
        saldo_total = self.bolsa_comun_disponible

        df_remanente['cupos_asignados_2E'] = 0  
        df_remanente['recurso_asignado_2E'] = 0.0
        df_remanente['saldo_total_remanente'] = 0.0

        
        for idx, row in df_remanente.iterrows():
            costo = row[COLUMNA_VALOR_PROGRAMA]
            cupos = min(row['numero_cupos_ofertar'], row[COLUMNA_CUPOS_MAXIMOS])
    
            if pd.isna(costo) or costo <= 0 or pd.isna(cupos) or cupos <= 0:
                df_remanente.at[idx, 'saldo_total_remanente'] = saldo_total
                continue
    
            recurso_necesario = costo * cupos
    
            if saldo_total >= recurso_necesario:
                df_remanente.at[idx, 'cupos_asignados_2E'] = cupos
                df_remanente.at[idx, 'recurso_asignado_2E'] = recurso_necesario
                saldo_total -= recurso_necesario
            else:
                
                cupos_posibles = saldo_total // costo
                recurso_asignado = cupos_posibles * costo
                
                df_remanente.at[idx, 'cupos_asignados_2E'] = cupos_posibles
                df_remanente.at[idx, 'recurso_asignado_2E'] = recurso_asignado
                saldo_total -= recurso_asignado
    
            df_remanente.at[idx, 'saldo_total_remanente'] = saldo_total
    
            if saldo_total <= 0:
                break
    
        self.bolsa_comun_disponible = saldo_total
        self.programas_remanantes = df_remanente

        self.recursos_asignados += df_remanente['recurso_asignado_remanente'].sum()

        return df_remanente
        