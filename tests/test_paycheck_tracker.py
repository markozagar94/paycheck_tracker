import unittest
from unittest.mock import patch, MagicMock
from paycheck_tracker import PaycheckTracker


class TestPaycheckTracker(unittest.TestCase):
    """
    Unit tests for the PaycheckTracker class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        # Mock environment variables and configurations
        self.email_subject = "Salary slip"
        self.email_label = "Paycheck"
        self.gmail_secret_name = "gmail-secret"
        self.project_id = "test-project"
        self.dataset_id = "test-dataset"
        self.table_id = "test-table"
        self.primary_key = "id"
        self.parser_config = {"Net Salary": "Net Salary:\\s*([\\d,]+)\\s*kn"}
        self.field_mapping = {"Net Salary": "net_salary"}

        # Create an instance of PaycheckTracker with mocked dependencies
        self.paycheck_tracker = PaycheckTracker(
            email_subject=self.email_subject,
            email_label=self.email_label,
            gmail_secret_name=self.gmail_secret_name,
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            table_id=self.table_id,
            primary_key=self.primary_key,
            parser_config=self.parser_config,
            field_mapping=self.field_mapping
        )

    @patch("paycheck_tracker.EmailClient")
    @patch("paycheck_tracker.BigQueryClient")
    def test_process_emails_no_emails(self, mock_bigquery_client, mock_email_client):
        """
        Test process_emails when no emails are found.
        """
        # Mock EmailClient to return no emails
        mock_email_client.return_value.fetch_emails.return_value = []

        # Run the method
        self.paycheck_tracker.process_emails()

        # Assertions
        mock_email_client.return_value.fetch_emails.assert_called_once()
        mock_bigquery_client.return_value.load_historical_data.assert_not_called()
        mock_bigquery_client.return_value.merge_incremental_data.assert_not_called()

    @patch("paycheck_tracker.EmailClient")
    @patch("paycheck_tracker.BigQueryClient")
    @patch("paycheck_tracker.SalaryParser")
    def test_process_emails_with_emails(self, mock_salary_parser, mock_bigquery_client, mock_email_client):
        """
        Test process_emails when emails are found and processed.
        """
        # Mock EmailClient to return a single email with an attachment
        mock_email = {
            "id": "test-email-id",
            "payload": {"parts": [{"filename": "salary.pdf"}]}
        }
        mock_email_client.return_value.fetch_emails.return_value = [mock_email]
        mock_email_client.return_value.download_attachment.return_value = ["salary.pdf"]

        # Mock SalaryParser to return parsed data
        mock_salary_parser.return_value.parse_salary_text.return_value = {"Net Salary": "1000"}

        # Mock BigQueryClient
        mock_bigquery_client_instance = mock_bigquery_client.return_value

        # Run the method
        self.paycheck_tracker.process_emails()

        # Assertions
        mock_email_client.return_value.fetch_emails.assert_called_once()
        mock_email_client.return_value.download_attachment.assert_called_once_with("test-email-id")
        mock_salary_parser.return_value.parse_salary_text.assert_called_once()
        mock_bigquery_client_instance.load_historical_data.assert_called_once()

    @patch("paycheck_tracker.EmailClient")
    @patch("paycheck_tracker.BigQueryClient")
    @patch("paycheck_tracker.SalaryParser")
    def test_process_emails_incremental_load(self, mock_salary_parser, mock_bigquery_client, mock_email_client):
        """
        Test process_emails with incremental load (only the latest email).
        """
        # Mock EmailClient to return multiple emails
        mock_emails = [
            {"id": "email-1", "payload": {"parts": [{"filename": "salary1.pdf"}]}},
            {"id": "email-2", "payload": {"parts": [{"filename": "salary2.pdf"}]}}
        ]
        mock_email_client.return_value.fetch_emails.return_value = mock_emails
        mock_email_client.return_value.download_attachment.return_value = ["salary2.pdf"]

        # Mock SalaryParser to return parsed data
        mock_salary_parser.return_value.parse_salary_text.return_value = {"Net Salary": "2000"}

        # Mock BigQueryClient
        mock_bigquery_client_instance = mock_bigquery_client.return_value

        # Run the method with incremental load
        self.paycheck_tracker.process_emails(historical_load=False)

        # Assertions
        mock_email_client.return_value.fetch_emails.assert_called_once()
        mock_email_client.return_value.download_attachment.assert_called_once_with("email-2")
        mock_salary_parser.return_value.parse_salary_text.assert_called_once()
        mock_bigquery_client_instance.merge_incremental_data.assert_called_once()

    @patch("paycheck_tracker.EmailClient")
    @patch("paycheck_tracker.BigQueryClient")
    @patch("paycheck_tracker.SalaryParser")
    def test_process_emails_multiple_attachments(self, mock_salary_parser, mock_bigquery_client, mock_email_client):
        """
        Test process_emails when an email has multiple attachments.
        """
        # Mock EmailClient to return an email with multiple attachments
        mock_email = {
            "id": "test-email-id",
            "payload": {"parts": [{"filename": "salary1.pdf"}, {"filename": "salary2.pdf"}]}
        }
        mock_email_client.return_value.fetch_emails.return_value = [mock_email]
        mock_email_client.return_value.download_attachment.return_value = ["salary1.pdf", "salary2.pdf"]

        # Run the method
        self.paycheck_tracker.process_emails()

        # Assertions
        mock_email_client.return_value.fetch_emails.assert_called_once()
        mock_email_client.return_value.download_attachment.assert_called_once_with("test-email-id")
        mock_salary_parser.return_value.parse_salary_text.assert_not_called()
        mock_bigquery_client.return_value.load_historical_data.assert_not_called()

    @patch("paycheck_tracker.EmailClient")
    @patch("paycheck_tracker.BigQueryClient")
    @patch("paycheck_tracker.SalaryParser")
    def test_process_emails_file_deletion_error(self, mock_salary_parser, mock_bigquery_client, mock_email_client):
        """
        Test process_emails when file deletion fails.
        """
        # Mock EmailClient to return a single email with an attachment
        mock_email = {
            "id": "test-email-id",
            "payload": {"parts": [{"filename": "salary.pdf"}]}
        }
        mock_email_client.return_value.fetch_emails.return_value = [mock_email]
        mock_email_client.return_value.download_attachment.return_value = ["salary.pdf"]

        # Mock SalaryParser to return parsed data
        mock_salary_parser.return_value.parse_salary_text.return_value = {"Net Salary": "1000"}

        # Mock os.remove to raise an error
        with patch("os.remove", side_effect=OSError("File deletion failed")):
            # Run the method
            self.paycheck_tracker.process_emails()

        # Assertions
        mock_email_client.return_value.fetch_emails.assert_called_once()
        mock_email_client.return_value.download_attachment.assert_called_once_with("test-email-id")
        mock_salary_parser.return_value.parse_salary_text.assert_called_once()
        mock_bigquery_client.return_value.load_historical_data.assert_called_once()


if __name__ == "__main__":
    unittest.main()