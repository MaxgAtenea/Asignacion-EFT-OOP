import pytest
import pandas as pd
import pandas.testing as pdt

from .utils import redondear_columnas
from asignacion.nuevos import AsignacionNuevos

@pytest.mark.parametrize("fixture_path", [
    ("tests/fixtures/nuevos_recursos_esperados.xlsx")
])
def test_asignar_recursos(fixture_path):
    """
    Test para la función asignar_recursos()
    """
    df_ejemplo = pd.read_excel(fixture_path).sort_values("cod_CNO").reset_index(drop=True)
    
    asignador = AsignacionNuevos(df_ejemplo, "nuevos")
    asignador.recursos_iniciales = 1000
    asignador.asignar_recursos()
    
    pass
