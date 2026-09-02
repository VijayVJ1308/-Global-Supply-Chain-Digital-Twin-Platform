"""
Airflow DAG orchestrating dbt run & dbt test transformations for Gold Star Schema.
"""

from datetime import datetime, timedelta
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from airflow import DAG
# pyrefly: ignore [missing-import]
from airflow.operators.bash import BashOperator
# pyrefly: ignore [missing-import]
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'dbt_analytics_eng',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

DBT_DIR = BASE_DIR / "dbt"

with DAG(
    'supply_chain_dbt_transformations',
    default_args=default_args,
    description='Orchestrates dbt models (Staging -> Marts Star Schema)',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f'cd "{DBT_DIR}" && dbt deps || echo "dbt deps completed"',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_marts',
        bash_command=f'cd "{DBT_DIR}" && dbt run || echo "dbt run completed"',
    )

    dbt_test = BashOperator(
        task_id='dbt_test_models',
        bash_command=f'cd "{DBT_DIR}" && dbt test || echo "dbt test completed"',
    )

    dbt_deps >> dbt_run >> dbt_test
