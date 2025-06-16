RECURSOS_POR_RUTA = {
    "antiguos":  1_320_000_000,
    "nuevos": 990_000_000,
    "cerrados": 990_000_000
}

# Columna que especifica el valor del programa indexado
COLUMNA_VALOR_PROGRAMA = "valor_programa_indexado"
# Columna que especifica el numero de cupos maximos aprobados 
COLUMNA_CUPOS_MAXIMOS = "numero_maximo_cupos"

MINIMO_CUPOS_CERRADOS_SEDE = 50

NOMBRE_COLUMNAS_MAPPING_EXTERNO = {
    "CÓDIGO DE INSTITUCIÓN ": 'codigo_institucion',
    "CÓDIGO SIET DEL PROGRAMA A OFERTAR (SOLO APLICA PARA PROGRAMAS ANTIGUOS)": 'codigo_programa',
    "NOMBRE PROGRAMA SEGÚN REGISTRO SECRETARÍA DE EDUCACIÓN" : 'nombre_programa',
    "NOMBRE DE LA INSTITUCÓN (INFORMACIÓN OBTENIDA DE SIET)" : "nombre_institucion",
    "NÚMERO DE CUPOS A OFERTAR": "numero_cupos_ofertar",
    "DURACIÓN DEL PROGRAMA EN NÚMERO DE HORAS (según aplique):" : "duracion_horas_programa",
    "DIRECCIÓN DE LA SEDE DONDE SE IMPARTIRÁ EL PROGRAMA" : "direccion_sede",
    "ISOEFT" : "isoeft",
    "Ocupación": "ocupacion",
    "IPO": "ipo",
    "Ruta habilitada": "ruta_habilitada",
    "VALOR TOTAL DEL PROGRAMA INDEXADO": "valor_programa_indexado",
    "Número máximo de cupos por grupos": "numero_maximo_cupos"
}

NOMBRE_COLUMNAS_MAPPING_COMPLEMENTO = {
    "Ocupacion": "_ocupacion",
    "ISOEFT_4d": "isoeft_4d",
    "CODIGO_PROGRAMA": "codigo_programa"
}


TIPO_COLUMNAS_MAPPING_EXTERNO = {
    "codigo_institucion": "Int64",
    "codigo_programa" : 'Int64', # la llave para unir Programas_EFT y Programas_EFT_Oferta
    "nombre_programa" : "str",
    "nombre_institucion" : "str",
    "numero_cupos_ofertar" : "Int64" , 
    "duracion_horas_programa": "Int64",
    "direccion_sede": "str",
    "isoeft" : "float",
    "ocupacion": "str",
    "ipo": "float",
    "ruta_habilitada" : "str",
    "valor_programa_indexado" : "float",
    "numero_maximo_cupos": "Int64"
}

TIPO_COLUMNAS_MAPPING_COMPLEMENTO = {
    'codigo_programa' : "Int64",
    "cod_CNO" : "Int64",
    "cod_CNO3d": "Int64",
    "cod_CNO2d": "Int64",
    "cod_CNO1d": "Int64",
    "isoeft_4d" : "float",
    "_ocupacion": "str",
}


# Columnas para quedarse con la data complementaria
COLUMNAS_COMPLEMENTO = [
    'cod_CNO',
    'cod_CNO3d',
    'cod_CNO2d',
    'cod_CNO1d',
    '_ocupacion',
    'isoeft_4d',
    'codigo_programa'
]

#son las columnas que queremos manipular en todo el proceso
COLUMNAS_EXTERNO = [
    'ruta_habilitada',
    'nombre_institucion',
    'ocupacion',
    'nombre_programa',
    'codigo_programa',
    'ipo',
    'Puntaje (nuevos y cerrados)',
    'Meta de vinculación',
    COLUMNA_VALOR_PROGRAMA,
    "numero_cupos_ofertar",
    'duracion_horas_programa',
    COLUMNA_CUPOS_MAXIMOS
]

#diccionario con los cno e IPO de los programas nuevos
PROGRAMA_INFO = {
    "TÉCNICO LABORAL COMO ASESOR COMERCIAL Y DE SERVICIOS": (6311, 0.524),
    "TÉCNICO LABORAL POR COMPETENCIAS ACOMPAÑANTES DOMICILIARIOS": (6371, 0.492),
    "Técnico Laboral por competencias en Codificación de Software": (2281, 0.665),
    "TECNICO LABORAL EN AUXILIAR DE ENFERMERÍA": (3311, 0.477),
    "TECNICO LABORAL EN ASISTENCIA Y SOPORTE DE TECNOLOGIAS DE LA INFORMACION": (2281, 0.665),
    "TECNICO LABORAL EN MANEJO DE HERRAMIENTAS PARA LA CODIFICACION DE SOFTWARE": (2281, 0.665),
    "TÉCNICO LABORAL EN AUXILIAR CLÍNICA VETERINARIA": (6374, 0.558),
    "TÉCNICO LABORAL AUXILIAR EN AUTOMATIZACIÓN E INSTRUMENTACIÓN INDUSTRIAL": (2321, 0.551),
    "TÉCNICO LABORAL AUXILIAR EN RECREACIÓN Y DEPORTE": (6642, 0.546),
    "TÉCNICO LABORAL AUXILIAR AGENTE DE VENTAS Y PUBLICIDAD": (6233, 0.523),
    "TÉCNICO LABORAL EN SOPORTE Y MANTENIMIENTO DE TI": (2281, 0.665),
    "TÉCNICO LABORAL EN AUXILIAR DE SISTEMAS INFORMÁTICOS": (8325, 0.502)
}




    
