# Paycheck Tracker

## Overview
Paycheck Tracker is a Python-based application designed to automate the extraction, parsing, and storage of salary data from emails containing PDF attachments. The extracted salary details are stored in Google BigQuery for further analysis and reporting.

## Features
- **Email Fetching**: Retrieves salary-related emails from Gmail based on subject and label.
- **PDF Parsing**: Extracts salary details (net salary, gross salary, tax, etc.) from PDF attachments.
- **Currency Conversion**: Converts salary amounts from Croatian Kuna (kn) to Euros (€) using a fixed exchange rate.
- **BigQuery Integration**: Stores structured salary data in Google BigQuery for easy querying and analysis.
- **Flexible Data Loading**: Supports both historical and incremental data loads.

## Tech Stack
- **Python**: Core programming language.
- **Google APIs**: Gmail API, BigQuery API, and Secret Manager for secure credential handling.
- **BigQuery**: Scalable data storage and analytics.

## Installation
### Prerequisites
Before you begin, ensure you have the following:
- **Python 3.8+** installed.
- **Google Cloud SDK** configured.
- A **BigQuery** dataset and table set up in your Google Cloud project.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/markozagar94/paycheck_tracker
   cd paycheck-tracker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Google Cloud credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```
4. Configure environment variables (update `.env` or export manually):
   ```bash
   export EMAIL_SUBJECT="Salary slip"
   export EMAIL_LABEL="Paycheck"
   export GMAIL_SECRET_NAME="your-secret-name"
   export PROJECT_ID="your-gcp-project-id"
   export DATASET_ID="your-dataset-id"
   export TABLE_ID="your-table-id"
   ```

5. Customize configuration files:

- Edit ```config.json``` to define parsing rules.
- Update ```salary_field_mapping.json``` to map PDF fields to structured output.

## Configuration Files
```config.json```
- This file defines the key-value pairs used to extract salary-related data from PDF files. 
- Each key represents a column name to search for in the PDF, and the corresponding value is a regex pattern to match the desired data.

**Example**:
```json
{
  "Net Salary": "Net Salary:\\s*([\\d,]+)\\s*€",
  "Gross Salary": "Gross Salary:\\s*([\\d,]+)\\s*€",
  "Tax": "Tax:\\s*([\\d,]+)\\s*€"
}
```
- Key: The name of the field to extract (e.g., "Net Salary").
- Value: A regex pattern to locate and extract the corresponding value from the PDF text.

```salary_field_mapping.json```
- This file maps the fields extracted from the PDF (defined in config.json) to the column names in the BigQuery table. 
- It ensures that the extracted data is stored in the correct BigQuery columns.

**Example**:
```json
{
  "Net Salary": "net_salary",
  "Gross Salary": "gross_salary",
  "Tax": "tax_amount"
}
```
- Key: The field name from config.json.
- Value: The corresponding column name in the BigQuery table.



## Usage
To run the application:
```bash
python main.py
```

## Testing
Run unit tests using:
```bash
pytest tests/
```
or with `unittest`:
```bash
python -m unittest discover tests/
```

## Project Structure
```
paycheck-tracker/
├── email_client.py           # Fetches emails and downloads PDFs
├── pdf_parser.py             # Extracts salary details from PDFs
├── bigquery_client.py        # Loads and merges data in BigQuery
├── paycheck_tracker.py       # Core logic for the application
├── main.py                   # Entry point of the application (fetches env vars and JSON configs)
├── config.json               # Parsing configuration
├── salary_field_mapping.json # Field mapping for structured output
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
│── tests/                    # Unit tests for all modules
│   ├── __init__.py
│   ├── test_email_client.py  
│   ├── test_pdf_parser.py 
│   ├── test_bigquery_client.py  
│── utils/
│   ├── __init__.py
│   ├── config_loader.py  # Loads JSON config files
│   ├── currency_utils.py # Currency conversion functions
│   ├── logging_utils.py  # Custom logging setup
│── pdf_files/
│   ├── Salary_slip_example.pdf
```

## Roadmap
- Add support for multi-currency conversion.
- Implement a web-based dashboard for salary visualization.
- Improve email parsing logic to handle various formats.

## Author
Marko Zagar

