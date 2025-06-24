import pandas as pd
from . import constants

from .nuevosyantiguos import AsignacionNuevosAntiguos

from .constants import COLUMNA_VALOR_PROGRAMA
from .constants import RECURSOS_POR_RUTA
from .constants import PROGRAMA_INFO

class AsignacionNuevos(AsignacionNuevosAntiguos):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Viejos'.
    #TODO: no debería hacerse el .apply(reemplazar_codigo,axis=1) si se pretende generalizar el codigo
    """

    def __init__(self, data):
        super().__init__(data, "nuevos")
        self.data = data
        self.data[['cod_CNO', 'ipo']] = self.data.apply(self._reemplazar_codCNO_ipo, axis=1)
        
        #Garantiza que al instanciar la clase, se calculen inmediatamente los recursos por cno.
        self.calcular_recursos_por_cno()
        #Ordenamos programas siguiendo criterios (condición necesaria y previa para la asignacion de recursos)
        self._ordenar_programas()
        #Garantiza que al instanciar la clase, se calcule la asignacion
        self.asignar_recursos()    
        #Identificar los programas con cupos disponibles después de la asignacion
        self._identificar_programas_disponibles()
        

    def asignar_recursos(self):
        """
        Implementa la lógica de asignación de recursos específica para la ruta 'Nuevos'.
        """
    
        data = self.data.copy()
        
        # Inicializar columna para cupos asignados
        data['cupos_asignados_2E'] = 0
        
        # Asignación iterativa por cod_CNO
        for cod_cno, grupo in data.groupby('cod_CNO'):
            
            recurso_total = grupo['recursosxcno'].iloc[0] #mismo recurso para cada ocupacion
            saldo = recurso_total
            indices = grupo.index
        
            for i in indices:
                costo_unitario = data.loc[i, COLUMNA_VALOR_PROGRAMA]
                cupos_disp = data.loc[i, 'numero_cupos_ofertar']
                if pd.isna(costo_unitario) or costo_unitario == 0:
                    continue
        
                recurso_necesario = cupos_disp * costo_unitario
        
                if saldo >= recurso_necesario:
                    data.loc[i, 'cupos_asignados_2E'] = cupos_disp
                    saldo -= recurso_necesario
                else:
                    cupos_asignables = saldo // costo_unitario
                    data.loc[i, 'cupos_asignados_2E'] = cupos_asignables
                    saldo -= cupos_asignables * costo_unitario
                    break
        
        # Paso 5: Calcular recursos asignados
        data['recurso_asignado_2E'] = data['cupos_asignados_2E'] * data[COLUMNA_VALOR_PROGRAMA]
        
        # Paso 6: Agrupar para obtener resumen de asignaciones por ocupacion
        asignacion_por_ocupacion = data.groupby('cod_CNO').agg(
            recurso_asignado_2E=('recurso_asignado_2E', 'sum'),
            cupos_asignados_2E=('cupos_asignados_2E', 'sum')
        ).reset_index()
        
        # Paso 5: Obtener recursos originales y número de cupos ofertados por las instituciones
        recursos_por_ocupacion = data.groupby('cod_CNO').agg(
            recursosxcno=('recursosxcno', 'first'),
            numero_cupos_ofertar=('numero_cupos_ofertar', 'sum')
        ).reset_index()
        
        
        # Paso 7: Agregar recursos estimados y calcular saldo no asignado
        asignacion_por_ocupacion = asignacion_por_ocupacion.merge(
            recursos_por_ocupacion, on='cod_CNO'
        )
        
        asignacion_por_ocupacion['Saldo_No_Asignado_2E'] = (
            asignacion_por_ocupacion['recursosxcno'] - asignacion_por_ocupacion['recurso_asignado_2E']
        )
        
        asignacion_por_ocupacion['cupos_no_asignados_2E'] = (
            asignacion_por_ocupacion['numero_cupos_ofertar'] - asignacion_por_ocupacion['cupos_asignados_2E']
        )
        
        self.recursos_asignados = asignacion_por_ocupacion['recurso_asignado_2E'].sum()
        self.recursos_disponibles -= self.recursos_asignados
        self.asignacion = asignacion_por_ocupacion

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


    def _reemplazar_codCNO_ipo(self, row):
        """
        Hardcode el valor de cod_CNO e ipo para los programas
        que se encuentran en el diccionario PROGRAMA_INFO.
        """
        programa = row['nombre_programa']
        if programa in PROGRAMA_INFO:
            return pd.Series(PROGRAMA_INFO[programa])
        return pd.Series([row['cod_CNO'], row['ipo']])

    def _identificar_programas_disponibles(self):
        """
        Identifica cuales programas después del la asignación quedaron con cupos disponibles.
        """
        data = self.asignacion.copy()
        
        nuevos_remanente = data[
            data['numero_cupos_ofertar'] - data['cupos_asignados_2E'] > 0
        ].reset_index(drop=True)

        self.programas_remanente = nuevos_remanente

    def _reasignar_remanente(self, columna_cupos= 'cupos_asignados_2E'):
        """
        Reasigna recursos disponibles (remanente) a los cupos de los programas que no han agotado sus cupos. 
        Esto se hace hasta agotar el saldo o completar los cupos pendientes.
        """
        df_remanente = self.programas_remanente.copy()
        saldo_total = self.bolsa_comun_disponible
    
        for idx, row in df_remanente.iterrows():
            cupos_restantes =  row['numero_cupos_ofertar'] - row[columna_cupos] 
            costo = row[columna_valor_programa]
    
            if pd.isna(costo) or costo <= 0 or pd.isna(cupos_restantes) or cupos_restantes <= 0:
                df_remanente.at[idx, 'saldo_total_remanente'] = saldo_total
                continue
    
            recurso_necesario = costo * cupos_restantes
    
            if saldo_total >= recurso_necesario:
                df_remanente.at[idx, 'cupos_asignados_remanente'] = cupos_restantes
                df_remanente.at[idx, 'recurso_asignado_remanente'] = recurso_necesario
                saldo_total -= recurso_necesario
            else:
                cupos_posibles = saldo_total // costo
                recurso_asignado = cupos_posibles * costo
    
                df_remanente.at[idx, 'cupos_asignados_remanente'] = cupos_posibles
                df_remanente.at[idx, 'recurso_asignado_remanente'] = recurso_asignado
                saldo_total -= recurso_asignado
    
            df_remanente.at[idx, 'saldo_total_remanente'] = saldo_total
    
            if saldo_total <= 0:
                break

        return df_remanente        

    