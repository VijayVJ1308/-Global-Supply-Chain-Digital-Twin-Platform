import pytest
from python.db.postgres_client import PostgresClient
from spark.batch.batch_medallion_etl import BatchMedallionETL

def test_medallion_tables_populated():
    pg = PostgresClient()
    
    # Check Silver tables
    df_sup = pg.read_df("SELECT COUNT(*) as cnt FROM silver.suppliers")
    assert df_sup["cnt"].iloc[0] > 0

    df_ord = pg.read_df("SELECT COUNT(*) as cnt FROM silver.orders")
    assert df_ord["cnt"].iloc[0] > 0

    # Check Gold Star Schema tables
    df_fact = pg.read_df("SELECT COUNT(*) as cnt FROM gold.fact_orders")
    assert df_fact["cnt"].iloc[0] > 0

    df_dim_date = pg.read_df("SELECT COUNT(*) as cnt FROM gold.dim_date")
    assert df_dim_date["cnt"].iloc[0] >= 365
