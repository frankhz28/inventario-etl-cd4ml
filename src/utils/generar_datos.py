import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generar_datos_condor(dias=180):
    """Genera datos sintéticos de ventas e inventario con patrones reales y quiebres de stock."""
    print(f"Generando {dias} días de datos históricos...")
    
    productos = ["PROD-CEMENTO", "PROD-LADRILLO", "PROD-ACERO", "PROD-ARENA"]
    clientes = ["CONSTRUCTORA ALFA", "CONSTRUCTORA BETA", "RETAIL OMEGA", "INDEPENDIENTE"]
    almacenes = ["ALM-LIMA", "ALM-CALLAO"]
    
    fecha_inicio = datetime.today() - timedelta(days=dias)
    fechas = [fecha_inicio + timedelta(days=i) for i in range(dias)]
    
    ventas_data = []
    inventario_data = []
    
    for fecha in fechas:
        for prod in productos:
            # 1. Simulamos el stock del día (con un 15% de probabilidad de quiebre de stock)
            hay_quiebre = np.random.choice([True, False], p=[0.15, 0.85])
            
            if hay_quiebre:
                stock_dia = 0
                ventas_dia = 0 # Si no hay stock, no hay venta
                estado = "CANCELADA_SIN_STOCK"
            else:
                # Si hay stock, generamos un stock aleatorio sano y ventas basadas en demanda normal
                stock_dia = int(np.random.normal(loc=1500, scale=300))
                ventas_dia = int(np.random.normal(loc=300, scale=80))
                # Aseguramos que la venta no supere el stock (lógica física)
                ventas_dia = max(0, min(ventas_dia, stock_dia)) 
                stock_dia -= ventas_dia # Restamos lo vendido para el cierre
                estado = "COMPLETADA"
            
            # Guardamos el registro de inventario (Stock de cierre)
            inventario_data.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "id_producto": prod,
                "stock_cierre": max(0, stock_dia),
                "almacen": np.random.choice(almacenes)
            })
            
            # Guardamos el registro de ventas (Puede haber de 1 a 3 ordenes por producto al día)
            if ventas_dia > 0:
                num_ordenes = np.random.randint(1, 4)
                ventas_divididas = [ventas_dia // num_ordenes] * num_ordenes
                
                for v in ventas_divididas:
                    ventas_data.append({
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "id_producto": prod,
                        "cantidad_vendida": v,
                        "cliente_b2b": np.random.choice(clientes),
                        "estado_orden": estado
                    })
            elif hay_quiebre:
                # Dejamos rastro del intento de compra fallido
                ventas_data.append({
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "id_producto": prod,
                    "cantidad_vendida": 0,
                    "cliente_b2b": np.random.choice(clientes),
                    "estado_orden": estado
                })

    # Convertimos a DataFrames
    df_ventas = pd.DataFrame(ventas_data)
    df_inventario = pd.DataFrame(inventario_data)
    
    # Aseguramos que la carpeta data/ exista
    os.makedirs("data", exist_ok=True)
    
    # Exportamos los CSVs
    df_ventas.to_csv("data/ventas_diarias.csv", index=False)
    df_inventario.to_csv("data/fotografia_inventario_diario.csv", index=False)
    
    print(f"Generados {len(df_ventas)} registros de ventas y {len(df_inventario)} de inventario.")

if __name__ == "__main__":
    np.random.seed(42)
    generar_datos_condor(180)