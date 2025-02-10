import json
import logging
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, NotFound
from typing import Dict, Any, List
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class BigQueryClient:
    """
    A client to interact with Google BigQuery, including table creation,
    data validation, and data loading (historical and incremental).
    """

    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        """
        Initializes the BigQuery client.

        Args:
            project_id (str): Google Cloud project ID.
            dataset_id (str): BigQuery dataset ID.
            table_id (str): BigQuery table ID.
        """
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    def create_table_if_not_exists(self, ddl_file: str):
        """
        Reads a DDL file and creates the table if it doesn't exist.

        Args:
            ddl_file (str): Path to the DDL SQL file.
        """
        try:
            with open(ddl_file, "r", encoding="utf-8") as f:
                ddl_query = f.read().replace("<PROJECT_ID>", self.project_id).replace("<DATASET_ID>", self.dataset_id)

            self.client.query(ddl_query).result()
            logging.info(f"Checked/created table: {self.full_table_id}")
        except BadRequest as e:
            logging.error(f"Invalid DDL query: {e}")
        except NotFound as e:
            logging.error(f"Dataset or table not found: {e}")
        except Exception as e:
            logging.error(f"Failed to create table: {e}")

    def load_historical_data(self, data: List[Dict[str, Any]]):
        """
        Loads all historical salary data into BigQuery in batches.

        Args:
            data (List[Dict[str, Any]]): The data to load.
        """

        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        try:
            list_data = data
            job = self.client.load_table_from_json(list_data, self.full_table_id, job_config=job_config)
            job.result()
            logging.info(f"Data loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise

    def merge_incremental_data(self, data: List[Dict[str, Any]]):
        """
        Merges incremental data into BigQuery, avoiding duplicates.

        Args:
            data (List[Dict[str, Any]]): The incremental data to merge.
        """

        temp_table_id = f"{self.full_table_id}_temp"
        table_schema = self.client.get_table(self.full_table_id).schema
        job_config = bigquery.LoadJobConfig(schema=table_schema, write_disposition="WRITE_TRUNCATE")

        try:
            # Load data into a temporary table
            list_data = data
            job = self.client.load_table_from_json(list_data, temp_table_id, job_config=job_config)
            job.result()

            # Merge data from the temporary table into the main table
            merge_query = f"""
            MERGE `{self.full_table_id}` AS target
            USING `{temp_table_id}` AS source
            ON target.salary_date = source.salary_date
            WHEN MATCHED THEN
              UPDATE SET target = source
            WHEN NOT MATCHED THEN
              INSERT ROW
            """
            self.client.query(merge_query).result()
            logging.info("Incremental data merged successfully.")

            # Delete the temporary table
            self.client.delete_table(temp_table_id)
            logging.info(f"Temporary table {temp_table_id} deleted.")
        except Exception as e:
            logging.error(f"Failed to merge incremental data: {e}")
