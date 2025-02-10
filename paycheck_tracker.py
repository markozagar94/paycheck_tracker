import os
import time
import logging
from typing import Dict, List, Any

from email_client import EmailClient
from pdf_parser import SalaryParser
from bigquery_client import BigQueryClient
from utils.currency_utils import convert_kn_to_eur


class PaycheckTracker:
    """
    A class to handle the extraction, parsing, and storage of salary data from emails.
    """

    def __init__(
        self,
        email_subject: str,
        email_label: str,
        gmail_secret_name: str,
        project_id: str,
        dataset_id: str,
        table_id: str,
        primary_key: str,
        parser_config: Dict[str, Any],
        field_mapping: Dict[str, str],
        output_dir: str = "pdf_files"
    ) -> None:
        """
        Initializes the PaycheckTracker with necessary configurations and clients.

        Args:
            email_subject (str): Subject of the emails to fetch.
            email_label (str): Label of the emails to fetch.
            gmail_secret_name (str): Name of the Gmail API secret in Secret Manager.
            project_id (str): Google Cloud project ID.
            dataset_id (str): BigQuery dataset ID.
            table_id (str): BigQuery table ID.
            primary_key (str): Primary key for the BigQuery table.
            parser_config (dict): Configuration for parsing PDFs.
            field_mapping (dict): Mapping of PDF fields to BigQuery columns.
            output_dir (str): Directory to save downloaded PDF files.
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Initialize Email Client
        self.email_client = EmailClient(
            subject_name=email_subject,
            label_name=email_label,
            secret_name=gmail_secret_name,
            output_dir=output_dir
        )

        # Store configurations
        self.parser_config = parser_config
        self.field_mapping = field_mapping

        # Initialize BigQuery Client
        self.bigquery_client = BigQueryClient(project_id, dataset_id, table_id, primary_key)

        # Ensure the table exists
        self.bigquery_client.create_table_if_not_exists("salary_data.ddl")

    def process_emails(self, historical_load: bool = True) -> None:
        """
        Processes emails by extracting and loading salary data into BigQuery.

        Args:
            historical_load (bool): Whether to perform full historical load or incremental.
        """
        # Fetch emails
        emails = self.email_client.fetch_emails()
        if not emails:
            logging.info("No salary emails found.")
            return

        # For incremental load, process only the latest email
        if not historical_load:
            logging.info("Incremental load! Fetching the attachment from the latest email.")
            emails = [emails[0]]

        # Process each email
        data_to_load = []
        for email in emails:
            email_id = email['id']
            logging.info(f"Processing email ID: {email_id}")

            # Download attachments
            attachment_names = self.email_client.download_attachment(email_id)
            if len(attachment_names) != 1:
                logging.warning(f"No documents or more than one attachment found in email {email_id}. Skipping...")
                continue

            attachment_name = attachment_names[0]
            logging.info(f"Downloaded attachment: {attachment_name}")

            # Parse the PDF
            pdf_parser = SalaryParser(attachment_name, self.parser_config)
            data = pdf_parser.parse_salary_text()
            data = convert_kn_to_eur(data)

            # Map fields to English column names
            mapped_data = {self.field_mapping.get(k, k): v for k, v in data.items()}
            mapped_data["file_name"] = os.path.basename(attachment_name)
            mapped_data["load_date"] = time.time()
            logging.info(f"Transformed data from attachment: {mapped_data}")

            data_to_load.append(mapped_data)

            # Clean up the downloaded file
            try:
                os.remove(attachment_name)
                logging.info(f"Deleted attachment: {attachment_name}")
            except OSError as e:
                logging.error(f"Failed to delete attachment {attachment_name}: {e}")

        # Load data into BigQuery
        if historical_load:
            logging.info("Loading historical data into BigQuery.")
            self.bigquery_client.load_historical_data(data_to_load)
        else:
            logging.info("Merging incremental data into BigQuery.")
            self.bigquery_client.merge_incremental_data(data_to_load)

    def run(self, historical_load: bool = True) -> None:
        """
        Main method to orchestrate the email processing and data loading.

        Args:
            historical_load (bool): Whether to perform full historical load or incremental.
        """
        self.process_emails(historical_load)