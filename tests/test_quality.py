import pytest
import pandas as pd
from python.db.postgres_client import PostgresClient
from python.quality.data_validator import DataValidator
from python.data_generator.generate_mock_data import main as run_generator
from spark.batch.batch_medallion_etl import BatchMedallionETL

@pytest.fixture(scope="module")
def setup_database():
    run_generator()
    etl = BatchMedallionETL()
    etl.run_pipeline()

def test_data_quality_framework(setup_database):
    validator = DataValidator()
    results = validator.run_all_checks()
    
    assert "summary" in results
    assert results["summary"]["total_tests"] > 0
    assert results["summary"]["score_pct"] >= 70.0
