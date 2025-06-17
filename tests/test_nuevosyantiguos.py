import pytest
import pandas as pd
import pandas.testing as pdt

from .utils import redondear_columnas
from asignacion.nuevosyantiguos import AsignacionNuevosAntiguos

from tests.data.parametros_test_nuevosyantiguos import test_cases_calcular_recursos_por_cno, ids_calcular_recursos_por_cno

def test_ponderar_ipo_ponderar_true():
    """
    Verifica que la función `_ponderar_ipo` calcule correctamente el IPO ponderado
    cuando `ponderar=True` y `alfa > 1`.

    El test valida:
    - Que el IPO se eleva al exponente `alfa` y se multiplica por el número de cupos
    - Que el cálculo es preciso para varios valores reales de `alfa` (e.g., 2 y 5.52)
    - Que la columna `ipo_ponderado` refleja correctamente la transformación convexa

    Casos de uso:
    - Ponderaciones no lineales (mayor prioridad a IPOs más altos)
    """
    df = pd.DataFrame({
        'id_programa': [1,2,3],
        'cod_CNO': [1111,1111, 2222],
        'ipo': [0.5, 0.6, 0.9],
        'numero_cupos_ofertar': [10, 20, 15]
    })

    asignador = AsignacionNuevosAntiguos(df, "nuevos")
    asignador._ponderar_ipo(alfa=2, ponderar=True)

    expected = df['numero_cupos_ofertar'] * (df['ipo'] ** 2)
    pd.testing.assert_series_equal(asignador.data['ipo_ponderado'], expected, check_names=False)

    expected = df['numero_cupos_ofertar'] * (df['ipo'] ** 5.52)
    asignador._ponderar_ipo(alfa=5.52, ponderar=True)
    pd.testing.assert_series_equal(asignador.data['ipo_ponderado'], expected, check_names=False)

def test_ponderar_ipo_ponderar_false():
    """
    Valida que la función `_ponderar_ipo` ignore la ponderación por cupos
    cuando `ponderar=False`.

    El test asegura que:
    - La columna `ipo_ponderado` sea igual al valor original de `ipo`
    - La transformación se comporta como una identidad, sin importar `alfa`

    Casos de uso:
    - Análisis exploratorio o modo "crudo" sin ponderación
    - Validación de comportamiento por defecto al desactivar la ponderación
    """    
    df = pd.DataFrame({
        'id_programa': [1,2,3],
        'cod_CNO': [1111,1111, 2222],
        'ipo': [0.5, 0.6, 0.9],
        'numero_cupos_ofertar': [10, 20, 15]
    })
    
    asignador = AsignacionNuevosAntiguos(df, "nuevos")
    asignador._ponderar_ipo(alfa=3.3, ponderar=False)
    pd.testing.assert_series_equal(asignador.data['ipo_ponderado'], df['ipo'], check_names=False)
    asignador._ponderar_ipo(alfa=1, ponderar=False)
    pd.testing.assert_series_equal(asignador.data['ipo_ponderado'], df['ipo'], check_names=False)



@pytest.mark.parametrize("alfa, ponderar, fixture_path", [
    (2, True, "tests/fixtures/esperado_alfa2.xlsx"),
    (1, True, "tests/fixtures/esperado_alfa1.xlsx")
])
def test_calcular_recursos_por_cno(alfa, ponderar, fixture_path):
    """
    Test parametrizado para validar el cálculo de recursos por cod_CNO 
    usando distintas combinaciones de `alfa` y `ponderar`, comparando el 
    resultado generado por el método `calcular_recursos_por_cno` con un 
    DataFrame esperado almacenado en archivo Excel.

    Este test cubre:
    - Caso general con múltiples CNOs y alfa > 1
    - Caso base con alfa = 1 (sin potenciación del IPO)

    Parámetros:
        alfa (int or float): Exponente aplicado al IPO en la ponderación.
        ponderar (bool): Si True, pondera el IPO por cupos.
        fixture_path (str): Ruta del archivo `.xlsx` que contiene el 
            DataFrame esperado, validado manualmente.

    TODO: Verificar que los recursos asignados por cno coincida con la bolsa disponible
    """    
    df = pd.DataFrame({
        'id_programa': [1, 2, 3, 4, 5],
        'cod_CNO': [1111, 1111, 2222, 2222, 3333],
        'ipo': [0.5, 0.6, 0.6, 0.6, 0.2],
        'numero_cupos_ofertar': [10, 20, 15, 10, 10]
    })

    asignador = AsignacionNuevosAntiguos(df, "nuevos")
    asignador.recursos_iniciales = 100
    asignador.calcular_recursos_por_cno(alfa=alfa, ponderar=ponderar)

    df_resultado = asignador.recursosxcno.sort_values("cod_CNO").reset_index(drop=True)
    df_esperado = pd.read_excel(fixture_path).sort_values("cod_CNO").reset_index(drop=True)

    columnas_a_redondear = ['ipo_ponderado', 'ipo', 'participacion_ipo', 'recursosxcno']
    df_resultado = redondear_columnas(df_resultado, columnas_a_redondear, decimales=1)
    df_esperado = redondear_columnas(df_esperado, columnas_a_redondear, decimales=1)

    pdt.assert_frame_equal(
        df_resultado,
        df_esperado,
        check_dtype=False,
        check_like=True
    )

@pytest.mark.parametrize("alfa, ponderar, fixture_path", [
    (2, True, "tests/fixtures/esperado_alfa2_unico_cno.xlsx")
])
def test_calcular_recursos_por_cno_unico_cno(alfa, ponderar, fixture_path):
    """
    Test para verificar el cálculo de recursos cuando todos los programas 
    pertenecen al mismo cod_CNO (grupo único). Esto valida el comportamiento 
    en casos extremos donde no hay distribución entre múltiples grupos.

    TODO: Verificar que los recursos asignados por cno coincida con la bolsa disponible
    """
    #Crear Dataframe de prueba
    df = pd.DataFrame({
        'id_programa': [1, 2, 3, 4, 5],
        'cod_CNO': [1111, 1111, 1111, 1111, 1111],
        'ipo': [0.5, 0.6, 0.6, 0.6, 0.2],
        'numero_cupos_ofertar': [10, 20, 15, 10, 10]
    })

    # Ejecutar función objetivo
    asignador = AsignacionNuevosAntiguos(df, "nuevos")
    asignador.recursos_iniciales = 100
    asignador.calcular_recursos_por_cno(alfa=alfa, ponderar=ponderar)
    
    # Cargar fixture esperado y redondear
    df_resultado = asignador.recursosxcno.sort_values("cod_CNO").reset_index(drop=True)
    df_esperado = pd.read_excel(fixture_path).sort_values("cod_CNO").reset_index(drop=True)

    # Comparar los resultados
    columnas_a_redondear = ['ipo_ponderado', 'ipo', 'participacion_ipo', 'recursosxcno']
    df_resultado = redondear_columnas(df_resultado, columnas_a_redondear, decimales=1)
    df_esperado = redondear_columnas(df_esperado, columnas_a_redondear, decimales=1)

    pdt.assert_frame_equal(
        df_resultado,
        df_esperado,
        check_dtype=False,
        check_like=True
    )




    