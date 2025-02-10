import os
from paycheck_tracker import PaycheckTracker
from utils.config_loader import load_json_file


if __name__ == "__main__":
    # Fetch environment variables
    email_subject = os.getenv("EMAIL_SUBJECT", "Salary slip")
    email_label = os.getenv("EMAIL_LABEL", "Paycheck")
    gmail_secret_name = os.getenv("GMAIL_SECRET_NAME")
    project_id = os.getenv("PROJECT_ID")
    dataset_id = os.getenv("DATASET_ID")
    table_id = os.getenv("TABLE_ID")
    primary_key = os.getenv("PRIMARY_KEY")
    historical_load = os.getenv("HISTORICAL_LOAD", "true").lower() == "true"

    # Load JSON configurations
    parser_config = load_json_file("config.json")
    field_mapping = load_json_file("salary_field_mapping.json")

    # Create an instance of PaycheckTracker
    paycheck_tracker = PaycheckTracker(
        email_subject=email_subject,
        email_label=email_label,
        gmail_secret_name=gmail_secret_name,
        project_id=project_id,
        dataset_id=dataset_id,
        table_id=table_id,
        primary_key=primary_key,
        parser_config=parser_config,
        field_mapping=field_mapping
    )

    # Run the application
    paycheck_tracker.run(historical_load)