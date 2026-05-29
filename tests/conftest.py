import pytest
import pandas as pd

@pytest.fixture
def df_escenario_quiebre():
    """Mock estatico: 2 días sanos y 1 día de quiebre en medio."""
    return pd.DataFrame({
        "id_producto": ["PROD-A", "PROD-A", "PROD-A"],
        "cantidad_vendida": [500, 0, 100],
        "quiebre_stock": [0, 1, 0] 
    })

@pytest.fixture    
def df_dummy_inventario():
    return pd.DataFrame({
        "fecha": ["2023-10-01"], 
        "id_producto": ["DUMMY"], 
        "stock_cierre": [1], 
        "almacen": ["DUMMY"]
    })

@pytest.fixture
def df_dummy_ventas():
    return pd.DataFrame({
        "fecha": ["2023-10-01"], 
        "id_producto": ["DUMMY"], 
        "cantidad_vendida": [1], 
        "cliente_b2b": ["DUMMY"], 
        "estado_orden": ["DUMMY"]
    })


@pytest.fixture
def df_prueba_carga():
    return pd.DataFrame({
        "fecha": ["2023-10-01"],
        "id_producto": ["PROD-INTEGRACION"],
        "demanda_no_restringida": [500]
    })