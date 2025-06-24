import os
import pandas as pd
import warnings
from datetime import datetime
from . import constants
from .constants import COLUMNAS_EXTERNO
from .constants import COLUMNAS_COMPLEMENTO
from .constants import TIPO_COLUMNAS_MAPPING_COMPLEMENTO
from .constants import TIPO_COLUMNAS_MAPPING_EXTERNO
from .constants import NOMBRE_COLUMNAS_MAPPING_EXTERNO
from .constants import NOMBRE_COLUMNAS_MAPPING_COMPLEMENTO

from .utils import exportar_log_errores

class AsignacionBase:
    """
    ## TODO: Terminar de escribir el objetivo de la clase
    Clase base para la asignación de recursos a programas educativos.

    Esta clase contiene la interfaz y funcionalidades comunes para todas las rutas de asignación
    (antiguos, viejos, cerrados), tales como validaciones, carga de datos y operaciones genéricas.
    """

    def __init__(self, recursos_iniciales = 0):
        """
        Inicializa la asignación con los recursos disponibles específicos para la ruta.

        Parameters:
        - recursos_disponibles (int): Monto total de recursos disponibles
        """
        self.recursos_iniciales = recursos_iniciales
        self.recursos_asignados = 0
        self.recursos_disponibles = self.recursos_iniciales
        
        self.bolsa_comun_disponible = 0
        self.recursos_remanentes_asignados = 0 
        
        self.data = pd.DataFrame()
        self.asignacion = pd.DataFrame()
        self.programas_remanente = pd.DataFrame()
        
        self.__llave_cruce = "codigo_programa" #llave para cruzar los documentos crudos
        self.path_load = "../input/"
        self.path_export = "output/"
        self._subdirectorio_resultados = "results/"
        self._columnas_relevantes = COLUMNAS_EXTERNO + COLUMNAS_COMPLEMENTO
        self._errores_validacion = []
    
    # TO DO: En el contrato de la función está pendiente especificar las condiciones que se esperan de ruta_archivo_externo (archvio que viene de otra area)
    # TO DO: Definir si en esta función van las pruebas de 
    def __cargar_datos_crudos(self, nombre_archivo_externo, nombre_archivo_complementario=None):
        """
        Carga y preprocesa los datos de entrada necesarios para la asignación.
    
        Args:
            ruta_archivo_externo (str): Ruta a un archivo Excel (.xlsx). Debe existir y ser legible por pandas. Es el archivo que le envía otra área a SAIGC.
                
            ruta_archivo_complementario (str, optional): Ruta a un archivo Pickle (.pkl) que contiene datos complementarios.
                Este archivo debe existir y ser legible por pandas.
                Si no se proporciona, se omite la fusión con datos complementarios.
     
        Raises:
            FileNotFoundError: Si alguno de los archivos proporcionados no existe.
        """

        ruta_archivo_externo = self.path_load +  nombre_archivo_externo
        ruta_archivo_complementario = self.path_load + nombre_archivo_complementario
        
        #Validar que existe ruta_archivo_externo
        if not os.path.exists(ruta_archivo_externo):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo_externo}")
            
        # Cargar archivo principal
        Programas_EFT = pd.read_excel(ruta_archivo_externo)
        # Renombrar algunas columnas
        Programas_EFT = Programas_EFT.rename(columns=NOMBRE_COLUMNAS_MAPPING_EXTERNO)
        # Cambiar tipo de los datos de algunas columnas
        Programas_EFT = Programas_EFT.astype(TIPO_COLUMNAS_MAPPING_EXTERNO)
    
        # Si hay archivo complementario, cargar y combinar
        if ruta_archivo_complementario is not None:
            
            #Validar que existe el ruta_archivo_complementario
            if not os.path.exists(ruta_archivo_complementario):
                raise FileNotFoundError(f"No se encontró el archivo complementario: {ruta_archivo_complementario}")
                
            df_complementario = pd.read_pickle(ruta_archivo_complementario)
            df_complementario = df_complementario.rename(columns=NOMBRE_COLUMNAS_MAPPING_COMPLEMENTO)
            df_complementario = df_complementario.astype(TIPO_COLUMNAS_MAPPING_COMPLEMENTO)
            
            df_complementario = df_complementario[COLUMNAS_COMPLEMENTO]
            
            # Unir Programas_EFT y df_complementario
            Programas_EFT = Programas_EFT.merge(
                df_complementario,
                how='left',
                on=[self.__llave_cruce]
            )

            cruzaron = Programas_EFT['cod_CNO'].notna().sum()
            no_cruzaron = Programas_EFT['cod_CNO'].isna().sum()
            print(f"La llave es: {self.__llave_cruce}. Ver diccionario para mayor detalle.")
            print(f"Programas que cruzaron: {cruzaron}")
            print(f"Programas que NO cruzaron: {no_cruzaron}")
        
        # Guardar resultado como atributo de instancia
        self.data = Programas_EFT[self._columnas_relevantes]

    def validar_datos(self, nombre_archivo_externo, dict_nombres = NOMBRE_COLUMNAS_MAPPING_EXTERNO, dict_tipado = TIPO_COLUMNAS_MAPPING_EXTERNO) -> None:
        """
        ## TO DO: Validación para el archivo complementario
        
        Valida y logea los siguientes problemas de la data importada:
        1. Nombres con espacios en blanco extra
        2. Columnas faltantes
        3. Columnas con valores nulos
        4. Columnas con tipos de datos no esperados
    
        Guarda los resultados en self._errores_validacion como una lista de strings.
        """

        #Ruta con el archivo principal
        ruta_archivo_externo = self.path_load + nombre_archivo_externo
        
        # Cargar archivo principal
        df = pd.read_excel(ruta_archivo_externo)        
        
        #Listamos las columnas obligatorias
        columnas_requeridas = list(dict_nombres.keys())

        # 1. Verificar columnas con espacios al inicio o final
        columnas_con_espacios = [col for col in df.columns if col != col.strip()]
        if columnas_con_espacios:
            warnings.warn("Existen columnas con espacios adicionales", category=UserWarning)
            self._errores_validacion.append(
                f"Columnas con espacios al inicio o final: {columnas_con_espacios}"
            )
        
        # 2. Verificar columnas faltantes
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            warnings.warn(
                "Faltan columnas indispensables para el proceso de asignación. "
                "Debe asegurarse de que estén para continuar con el proceso",
                category=UserWarning
            )
            self._errores_validacion.append(
                f"Faltan columnas requeridas: {columnas_faltantes}"
            )
            exportar_log_errores(self._errores_validacion)
            #Se interrumpe el proceso
            return
        
        # 3. Verificar valores nulos en columnas requeridas
        columnas_con_nulos = df[columnas_requeridas].isnull().any()
        columnas_con_nulos = columnas_con_nulos[columnas_con_nulos].index.tolist()
        if columnas_con_nulos:
            warnings.warn("Existen columnas indispensables con valores nulos", category=UserWarning)
            self._errores_validacion.append(
                f"Columnas con valores nulos: {columnas_con_nulos}"
            )
        
        # 4. Verificar tipos de datos
        for col in dict_nombres.keys():
            tipo_actual = str(df[col].dtype)
            temp_col = dict_nombres[col]
            tipo_esperado = dict_tipado[temp_col]
            if tipo_esperado.lower() not in tipo_actual.lower():
                warnings.warn("Existen columnas indispensables con tipado no adecuado", category=UserWarning)
                self._errores_validacion.append(
                    f"Tipo incorrecto en '{col}': se esperaba '{tipo_esperado}', se encontró '{tipo_actual}'"
                )
                
        exportar_log_errores(self._errores_validacion)


        
    def crear_rutas(self, nombre_archivo_externo, nombre_archivo_complementario=None):
        """
        Crea un diccionario que contiene un DataFrame para cada ruta habilitada.
    
        Esta función carga los datos desde los archivos especificados y luego separa
        la información en distintos DataFrames, uno por cada valor único en la columna 
        'Ruta habilitada'. Cada DataFrame se guarda en un diccionario con el nombre de la ruta como clave.
    
        Parámetros:
            nombre_archivo_externo (str): Nombre o ruta del archivo principal con los datos habilitados.
            nombre_archivo_complementario (str, opcional): Nombre o ruta del archivo complementario 
                con información adicional (por defecto es None).
    
        Retorna:
            dict: Un diccionario donde las claves son los nombres de las rutas habilitadas y 
            los valores son los DataFrames correspondientes a cada ruta.
        """
        self.__cargar_datos_crudos(nombre_archivo_externo, nombre_archivo_complementario)
        
        ruta_labels = self.data['ruta_habilitada'].unique()

        # Crear un diccionario con un DataFrame por cada valor de ruta
        rutas_dict = {
            ruta: self.data.loc[self.data['ruta_habilitada'] == ruta].copy()
            for ruta in ruta_labels
        }
        
        return rutas_dict 

    def _actualizar_bolsa_comun(self,bolsa_antiguos, bolsa_nuevos, bolsa_cerrados):
        """
        Calcula la bolsa comun a partir de los recursos sobrantes de las 3 rutas.
        """
        self.bolsa_comun = bolsa_antiguos + bolsa_nuevos + bolsa_cerrados
                
        
    def asignar_recursos(self):
        """
        Ejecuta la lógica genérica de distribución de recursos de TODAS las rutas.
        """
        pass

    def exportar_resultado(self, path_salida):
        """
        Exporta el resultado de la asignación a un archivo.

        Parameters:
        - path_salida (str): Ruta del archivo de salida.
        """
        pass