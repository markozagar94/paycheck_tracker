import os
import time
import logging
from typing import Dict, List, Any

from email_client import EmailClient
from pdf_parser import SalaryParser
from bigquery_client import BigQueryClient
from utils.config_loader import load_json_file
from utils.currency_utils import convert_kn_to_eur

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_emails(
    email_client: EmailClient,
    parser_config: Dict[str, Any],
    field_mapping: Dict[str, str],
    bigquery_client: BigQueryClient,
    historical_load: bool = True
) -> None:
    """
    Processes emails by extracting and loading salary data into BigQuery.

    Args:
        email_client (EmailClient): Gmail API client instance.
        parser_config (dict): PDF parser configuration.
        field_mapping (dict): Field name mapping.
        bigquery_client (BigQueryClient): BigQuery client instance.
        historical_load (bool): Whether to perform full historical load or incremental.
    """
    # Fetch emails
    emails = email_client.fetch_emails()
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
        attachment_names = email_client.download_attachment(email_id)
        if len(attachment_names) != 1:
            logging.warning(f"No documents or more than one attachment found in email {email_id}. Skipping...")
            continue

        attachment_name = attachment_names[0]
        logging.info(f"Downloaded attachment: {attachment_name}")

        # Parse the PDF
        pdf_parser = SalaryParser(attachment_name, parser_config)
        data = pdf_parser.parse_salary_text()
        data = convert_kn_to_eur(data)

        # Map fields to English column names
        mapped_data = {field_mapping.get(k, k): v for k, v in data.items()}
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
        bigquery_client.load_historical_data(data_to_load)
    else:
        logging.info("Merging incremental data into BigQuery.")
        bigquery_client.merge_incremental_data(data_to_load)


def main() -> None:
    """
    Main function to orchestrate the email processing and data loading.
    """
    # Initialize Email Client
    email_client = EmailClient(
        subject_name=os.getenv("EMAIL_SUBJECT", "Salary slip"),
        label_name=os.getenv("EMAIL_LABEL", "Paycheck"),
        secret_name=os.getenv("GMAIL_SECRET_NAME"),
        output_dir="pdf_files"
    )

    # Load Configuration Files
    parser_config = load_json_file("config.json")
    field_mapping = load_json_file("salary_field_mapping.json")

    # Initialize BigQuery Client
    project_id = os.getenv("PROJECT_ID")
    dataset_id = os.getenv("DATASET_ID")
    table_id = os.getenv("TABLE_ID")
    primary_key = os.getenv("PRIMARY_KEY")
    bigquery_client = BigQueryClient(project_id, dataset_id, table_id, primary_key)

    # Ensure the table exists
    bigquery_client.create_table_if_not_exists("salary_table_ddl.sql")

    # Determine if historical or incremental load
    historical_load = os.getenv("HISTORICAL_LOAD", "true").lower() == "true"

    # Process Emails
    process_emails(email_client, parser_config, field_mapping, bigquery_client, historical_load)


if __name__ == "__main__":
    main()
