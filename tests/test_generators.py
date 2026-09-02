import pytest
import pandas as pd
from python.data_generator.generate_mock_data import generate_dataset

def test_generate_dataset_structure():
    data = generate_dataset(num_orders=50, num_iot_events=100)
    
    assert "suppliers" in data
    assert "warehouses" in data
    assert "products" in data
    assert "customers" in data
    assert "orders" in data
    assert "shipments" in data
    assert "inventory" in data
    assert "iot_sensors" in data

    df_orders = data["orders"]
    assert len(df_orders) == 50
    assert "order_id" in df_orders.columns
    assert "unit_price" in df_orders.columns

    df_iot = data["iot_sensors"]
    assert len(df_iot) == 100
    assert "temperature_c" in df_iot.columns
