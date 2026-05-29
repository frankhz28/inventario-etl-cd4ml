import pandas as pd

def extraer_df(ruta_archivo : str) -> pd.DataFrame:
    df = pd.read_csv(ruta_archivo)
    return df

def sanitizar_cv(ruta_archivo, num_columnas):
    lineas_limpias = []
    with open(ruta_archivo, 'r') as f:
        for linea in f:
            campos = linea.strip().split(',')
            campos_ajustados = campos[:num_columnas]
            linea_limpia = ','.join(campos_ajustados)
            lineas_limpias.append(linea_limpia)
            
    ruta_new_archivo = ruta_archivo.replace('.csv', '_sanitizado.csv')
            
    with open(ruta_new_archivo, 'w') as f:
        for linea in lineas_limpias:
            f.write(linea + '\n')
