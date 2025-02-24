from os import remove
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import timedelta, datetime



## Output current day for file exportation
output_name = datetime.now().strftime("%Y%m%d")



default_args = {"owner": "airflow", "depends_on_past": False, "retries": 1}

with DAG(
    dag_id="sp_etl_pipeline",
    description="Spotify ELT",
    schedule_interval= "@daily",
    default_args=default_args,
    start_date= days_ago(1),
    catchup=True,
    max_active_runs=1,
    tags=["SpotifyETL"],
) as dag:
    extract_sp_data = BashOperator(
        task_id = "extract_spotify_data",
        bash_command = f"python3 /opt/airflow/extraction/extract_playlist_sp.py {output_name}",
        dag = dag,
    )
    extract_sp_data.doc_md = "Extract Spotify playlist and track data, then store as CSV"
    load_to_s3 = BashOperator(
        task_id = "upload_to_s3_bucket",
        bash_command = f"python3 /opt/airflow/extraction/load_sp_to_s3.py {output_name}",
        dag = dag,
    )

    

extract_sp_data >> load_to_s3