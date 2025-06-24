import pandas as pd
from . import constants
from .constants import COLUMNA_VALOR_PROGRAMA
from .nuevosyantiguos import AsignacionNuevosAntiguos


class AsignacionAntiguos(AsignacionNuevosAntiguos):
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase encargada de gestionar la asignación de recursos para la ruta 'Antiguos'.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Inicializa la asignación con los recursos disponibles específicos para la ruta antiguos.

        Parameters:
        - data (pandas dataframe): Dataframe con la inforamcion de los programas Antiguos
        """
        super().__init__(data, "antiguos")
        #TODO: Definir contrato
        self.data = data
        
        #Atributos para guardar los recursos de la primera y segunda asignacion de recursos
        self.primera_asignacion = pd.DataFrame()
        self.segunda_asignacion = pd.DataFrame()

        
        #Garantiza que al instanciar la clase, se calculen inmediatamente los recursos por cno.
        self.calcular_recursos_por_cno()
        #Ordenamos por ISOEFT (condición necesaria para la asignacion de recursos)
        self.ordenar_ocupaciones_por_isoeft()
        #Garantiza que al instanciar la clase, se calcule la segunda asignacion e implicitamente la primera asignacion
        self.asignar_recursos_segunda_etapa()
        #Identificar los programas con cupos disponibles después de la asignacion
        self._identificar_programas_disponibles()      
        

    def ordenar_ocupaciones_por_isoeft(self):
        """
        ## TODO: Eliminar la posibilidad de que hayan NANS. Esto se debe corregir desde la fuente
        
        Ordena un DataFrame por ['cod_CNO', 'ocupacion', 'IPO', 'isoeft_4d'],
        asegurando que las filas con NaN en 'isoeft_4d' queden al final del DataFrame completo.

        """
        # Separar por presencia de NaN en isoeft_4d
        sin_nan = self.data[self.data['isoeft_4d'].notna()]
        con_nan = self.data[self.data['isoeft_4d'].isna()]
    
        #Columnas para ordenar
        columnas = [
            'ipo',
            'cod_CNO',
            'ocupacion',
            'isoeft_4d',
            COLUMNA_VALOR_PROGRAMA,
            "numero_cupos_ofertar",
            "duracion_horas_programa"
        ]
    
        orden = [
            False,
            True,
            True,
            False,
            True,
            False,
            True
        ]
        
        # Ordenar las filas válidas
        sin_nan = sin_nan.sort_values(
            columnas, 
            ascending= orden
        )
    
        # Concatenar
        self.data = pd.concat([sin_nan, con_nan], ignore_index=True)

    def _asignar_recursos_primera_etapa(self):
        """
        Asigna cupos y recursos por ocupacion según los lineamientos de la Ruta Antiguos, paso 2
    
        Retorna un resumen por ocupacion con cupos y recursos asignados, y los saldos no utilizados.
        """       
        data = self.data.copy()
        # Paso 1: Crear nueva columna para asignación
        data['cupos_asignados_2E'] = 0
    
        # Paso 2: Iterar por grupo de ocupacion para asignar los recursos disponibles
        for (cod_cno, ocupacion), grupo in data.groupby(['cod_CNO', 'ocupacion']):
            recurso_por_dispersar = grupo['recursosxcno'].iloc[0]
            saldo = recurso_por_dispersar
            indices = grupo.index
    
            for i in indices:
                costo_unitario = data.loc[i, COLUMNA_VALOR_PROGRAMA]
                cupos_disp = data.loc[i, 'numero_cupos_ofertar']

                ## TODO: Esta condicion deberia verificarse desde la fuente
                if pd.isna(costo_unitario) or costo_unitario == 0:
                    continue
    
                recurso_necesario = cupos_disp * costo_unitario
    
                if saldo >= recurso_necesario:
                    data.loc[i, 'cupos_asignados_2E'] = cupos_disp
                    saldo -= recurso_necesario
                else:
                    # Ver si se puede financiar al menos un cupo
                    cupos_asignables = saldo // costo_unitario
                    data.loc[i, 'cupos_asignados_2E'] = cupos_asignables
                    saldo -= cupos_asignables * costo_unitario
                    break
    
        # Paso 3: Calcular recursos efectivamente asignados por programa
        data['recurso_asignado_2E'] = data['cupos_asignados_2E'] * data[COLUMNA_VALOR_PROGRAMA]
    
        # Paso 4: Agrupar para obtener resumen de asignaciones por ocupacion
        asignacion_por_ocupacion = data.groupby(['cod_CNO', 'ocupacion']).agg(
            recurso_asignado_2E=('recurso_asignado_2E', 'sum'),
            cupos_asignados_2E=('cupos_asignados_2E', 'sum')
        ).reset_index()
    
        # Paso 5: Obtener recursos originales y número de cupos ofertados por las instituciones
        recursos_por_ocupacion = data.groupby(['cod_CNO', 'ocupacion']).agg(
            recursosxcno=('recursosxcno', 'first'),
            numero_cupos_ofertar=('numero_cupos_ofertar', 'sum')
        ).reset_index()
    
        # Paso 6: Unir ambas tablas
        asignacion_por_ocupacion = asignacion_por_ocupacion.merge(
            recursos_por_ocupacion, on=['cod_CNO', 'ocupacion']
        )
    
        # Paso 7: Calcular saldos no asignados
        asignacion_por_ocupacion['Saldo_No_Asignado_2E'] = (
            asignacion_por_ocupacion['recursosxcno'] - asignacion_por_ocupacion['recurso_asignado_2E']
        )
    
        asignacion_por_ocupacion['cupos_no_asignados_2E'] = (
            asignacion_por_ocupacion['numero_cupos_ofertar'] - asignacion_por_ocupacion['cupos_asignados_2E']
        )

        self.recursos_asignados = asignacion_por_ocupacion['recurso_asignado_2E'].sum()
        self.recursos_disponibles -= self.recursos_asignados
        self.primera_asignacion = data
        
        return asignacion_por_ocupacion
        
    def asignar_recursos_segunda_etapa(self):
        """
        Asigna recursos sobrantes de la segunda etapa a programas priorizados en una tercera etapa,
        usando una bolsa común. Actualiza el DataFrame original con asignaciones adicionales.
        # TODO: 
            1. En el tests assert si data['Saldo_Remanente_3E'] == self.recursos_disponibles
        """
        
        asignacion_por_ocupacion = self._asignar_recursos_primera_etapa()

        #saldo_comun_3E = asignacion_por_ocupacion['Saldo_No_Asignado_2E'].sum()
        saldo_comun_3E = self.recursos_disponibles
        
        
        data = self.primera_asignacion.copy()
        
        data['cupos_asignados_3E'] = 0
        data['recurso_asignado_3E'] = 0.0
        
        #TODO: verificar en el test si ordenar_por_isoeft es redundante | acondicionarla para la clase:
        #      data = ordenar_ocupaciones_por_isoeft(data)
    
        for idx, row in data.iterrows():
            costo = row[COLUMNA_VALOR_PROGRAMA]
            cupos = row['numero_cupos_ofertar']
            if pd.isna(costo) or costo <= 0 or pd.isna(cupos) or cupos <= 0:
                continue
    
            recurso_necesario = costo * cupos
            
            if saldo_comun_3E >= recurso_necesario:
                data.at[idx, 'cupos_asignados_3E'] = cupos
                data.at[idx, 'recurso_asignado_3E'] = recurso_necesario
                saldo_comun_3E -= recurso_necesario
            else:
                cupos_posibles = saldo_comun_3E // costo
                if cupos_posibles >= 1:
                    recurso_asignado = cupos_posibles * costo
                    data.at[idx, 'cupos_asignados_3E'] = cupos_posibles
                    data.at[idx, 'recurso_asignado_3E'] = recurso_asignado
                    saldo_comun_3E -= recurso_asignado
                else:
                    break
    
        data['Total_Cupos_Asignados'] = data['cupos_asignados_2E'] + data['cupos_asignados_3E']
        data['Total_Recurso_Asignado'] = data['recurso_asignado_2E'] + data['recurso_asignado_3E']
        data['Saldo_Remanente_3E'] = saldo_comun_3E

        self.recursos_disponibles -= data['recurso_asignado_3E'].sum()
        self.recursos_asignados += data['recurso_asignado_3E'].sum()
        
        
        self.segunda_asignacion = data    
        self.asignacion = data
        
    def _identificar_programas_disponibles(self):
        """
        Identifica cuales programas después del la asignación quedaron con cupos disponibles.
        """        
        data = self.asignacion.copy()
        
        antiguos_remanente = data[
            data['numero_cupos_ofertar'] - data['Total_Cupos_Asignados'] > 0
        ].reset_index(drop=True)
        
        self.programas_remanente = antiguos_remanente

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

