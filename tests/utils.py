import pandas as pd

def redondear_columnas(df, columnas, decimales=1):
    """
    Redondea las columnas especificadas en el DataFrame a un número de decimales.

    Parámetros:
        df (pd.DataFrame): El DataFrame original.
        columnas (list): Lista de nombres de columnas a redondear.
        decimales (int): Cantidad de decimales (por defecto 1).

    Retorna:
        pd.DataFrame: copia del DataFrame con columnas redondeadas.
    """
    df = df.copy()
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].round(decimales)
    return df
