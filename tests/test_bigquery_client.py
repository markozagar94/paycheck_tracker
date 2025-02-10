import os
import unittest
from unittest.mock import MagicMock, patch
from bigquery_client import BigQueryClient


class TestBigQueryClient(unittest.TestCase):
    def setUp(self):
        """Set up test environment and initialize BigQueryClient."""
        self.project_id = os.getenv("PROJECT_ID", "test_project")
        self.dataset_id = os.getenv("DATASET_ID", "test_dataset")
        self.table_id = os.getenv("TABLE_ID", "test_table")
        self.primary_key = os.getenv("PRIAMRY_KEY", "primary_key")

        self.client = BigQueryClient(self.project_id, self.dataset_id, self.table_id, self.primary_key)
        self.client.client = MagicMock()  # Mock BigQuery client

    def test_create_table_if_not_exists(self):
        """Test creating a table if it does not exist."""
        ddl_file = "test_table.ddl"
        with patch("builtins.open", unittest.mock.mock_open(read_data="CREATE TABLE test_table (id INT64)")):
            self.client.create_table_if_not_exists(ddl_file)
            self.client.client.query.assert_called()

    def test_load_historical_data(self):
        """Test loading historical data into BigQuery."""
        self.client.validate_schema = MagicMock(return_value=True)
        self.client.client.load_table_from_json.return_value.result = MagicMock()

        data = [{"id": 1, "salary": 1000}]
        self.client.load_historical_data(data)
        self.client.client.load_table_from_json.assert_called()

    def test_merge_incremental_data(self):
        """Test merging incremental data into BigQuery."""
        self.client.validate_schema = MagicMock(return_value=True)
        self.client.client.get_table.return_value.schema = [MagicMock(name="id"), MagicMock(name="salary")]
        self.client.client.load_table_from_json.return_value.result = MagicMock()
        self.client.client.query.return_value.result = MagicMock()

        data = [{"id": 1, "salary": 2000}]
        self.client.merge_incremental_data(data)
        self.client.client.load_table_from_json.assert_called()
        self.client.client.query.assert_called()
        self.client.client.delete_table.assert_called()


if __name__ == '__main__':
    unittest.main()
