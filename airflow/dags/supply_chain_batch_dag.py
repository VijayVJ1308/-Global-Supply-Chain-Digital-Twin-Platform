from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
from python.data_generator.generate_mock_data import main as run_data_generator
from spark.batch.batch_medallion_etl import BatchMedallionETL
from python.quality.data_validator import DataValidator

default_args = {
    'owner': 'supply_chain_data_eng',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def task_ingest_bronze():
    print("Executing Batch Data Ingestion into Bronze Layer...")
    run_data_generator()

def task_transform_medallion():
    print("Executing Medallion ETL Pipeline (Bronze -> Silver -> Gold)...")
    etl = BatchMedallionETL()
    etl.run_pipeline()

def task_data_quality_audit():
    print("Running Automated Data Quality Audit...")
    validator = DataValidator()
    results = validator.run_all_checks()
    if results['summary']['score_pct'] < 70.0:
        raise ValueError(f"Data Quality Score below SLA threshold: {results['summary']['score_pct']}%")

with DAG(
    'global_supply_chain_batch_pipeline',
    default_args=default_args,
    description='Production Global Supply Chain Medallion Lakehouse Batch ETL',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    ingest = PythonOperator(
        task_id='ingest_raw_bronze',
        python_callable=task_ingest_bronze,
    )

    transform = PythonOperator(
        task_id='transform_medallion_lakehouse',
        python_callable=task_transform_medallion,
    )

    quality_audit = PythonOperator(
        task_id='verify_data_quality_sla',
        python_callable=task_data_quality_audit,
    )

    ingest >> transform >> quality_audit
