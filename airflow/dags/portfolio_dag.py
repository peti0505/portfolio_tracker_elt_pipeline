from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
from docker.types import Mount
import os

project_path = os.environ.get("project_file_path")

with DAG(
    "portfolio_dag",
    start_date=datetime(2026, 5, 20),
    schedule_interval="0 2 * * *",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(hours=1)},
) as dag:

    extract_load = DockerOperator(
        task_id="extract_load",
        image="portfolio_extract_load:latest",
        docker_url="unix://var/run/docker.sock",
        mounts=[
            Mount(
                source=f"{project_path}/gcp_key.json",
                target="/extract_load/gcp_key.json",
                type="bind",
            ),
            Mount(
                source=f"{project_path}/python_logs",
                target="/extract_load/python_logs",
                type="bind",
            ),
            Mount(
                source=f"{project_path}/.env",
                target="/extract_load/.env",
                type="bind",
            ),
        ],
        auto_remove=True,
    )

    dbt_modeling = DockerOperator(
        task_id="dbt_modeling",
        image="portfolio_dbt_modeling:latest",
        docker_url="unix://var/run/docker.sock",
        environment={
            "project_id": os.environ.get("project_id"),
            "dataset_name": os.environ.get("dataset_name"),
        },
        mounts=[
            Mount(
                source=f"{project_path}/gcp_key.json",
                target="/modeling/gcp_key.json",
                type="bind",
            ),
            Mount(
                source=f"{project_path}/profiles.yml",
                target="/root/.dbt/profiles.yml",
                type="bind",
            ),
        ],
        auto_remove=True,
        retries=2,
        retry_delay=timedelta(minutes=5)
    )

    extract_load >> dbt_modeling
