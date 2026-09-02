from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator
from python.quality.data_validator import DataValidator

default_args = {
    'owner': 'data_quality_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def run_quality_suite():
    validator = DataValidator()
    results = validator.run_all_checks()
    print(f"Data Quality Audit Completed. Summary: {results['summary']}")

with DAG(
    'supply_chain_data_quality_hourly',
    default_args=default_args,
    description='Hourly data freshness, completeness, and referential integrity audit',
    schedule_interval='@hourly',
    catchup=False,
) as dag:

    audit_task = PythonOperator(
        task_id='run_data_quality_suite',
        python_callable=run_quality_suite,
    )
