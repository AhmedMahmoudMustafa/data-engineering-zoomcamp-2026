from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
default_args = {
    'owner': 'ahmed',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='fraud_detection_pipeline',
    default_args=default_args,
    description='Fraud detection pipeline: GCS -> BigQuery -> dbt',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['fraud', 'capstone'],
) as dag:

    # load_to_bigquery = BashOperator(
    #     task_id='load_gcs_to_bigquery',
    #     bash_command="""
    #     bq load \
    #       --source_format=PARQUET \
    #       --location=EU \
    #       capsone-project-492612:capsone_findata_dataset.transactions_raw \
    #       "gs://de-capstone-bucket-findata/raw/transactions/*.parquet"
    #     """,
    # )

    load_to_bigquery = GCSToBigQueryOperator(
    task_id='load_gcs_to_bigquery',
    bucket='de-capstone-bucket-findata',
    source_objects=['raw/transactions/*'],
    destination_project_dataset_table='capsone-project-492612.capsone_findata_dataset.transactions_raw',
    source_format='PARQUET',
    write_disposition='WRITE_TRUNCATE',
    location='EU', # Change to 'US' if your dataset is in the US
    gcp_conn_id='google_cloud_default',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/fraud_analytics && dbt run --profiles-dir /opt/airflow/fraud_analytics',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/fraud_analytics && dbt test --profiles-dir /opt/airflow/fraud_analytics',
    )

    notify_done = BashOperator(
        task_id='notify_done',
        bash_command='echo "Pipeline completed successfully at $(date)"',
    )

    load_to_bigquery >> dbt_run >> dbt_test >> notify_done
