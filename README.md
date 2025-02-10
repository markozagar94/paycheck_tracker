# Paycheck Tracker

## Overview
Paycheck Tracker is a Python-based application that automates the extraction, parsing, and storage of salary data from emails containing PDF attachments. The extracted salary details are stored in Google BigQuery for further analysis.

## Features
- Fetches salary emails from Gmail based on subject and label.
- Extracts salary details (net salary, gross salary, tax, etc.) from PDF attachments.
- Converts salary amounts from Croatian Kuna (kn) to Euros (€) using a fixed exchange rate.
- Loads salary data into Google BigQuery for structured storage.
- Supports both historical and incremental data loads.

## Tech Stack
- **Python** (core language)
- **Google APIs** (Gmail API, BigQuery API, Secret Manager)
- **BigQuery** (data storage)

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Google Cloud SDK
- BigQuery set up with the necessary dataset and table

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/paycheck-tracker.git
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

5. Edit the config.json, salary_field_mapping.json according to your PDF document :

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
├── __init__.py
├── email_client.py           # Fetches emails and downloads PDFs
├── pdf_parser.py             # Extracts salary details from PDFs
├── bigquery_client.py        # Loads and merges data in BigQuery
├── main.py                   # Entry point of the application
├── config.json               # Parsing configuration
├── salary_field_mapping.json # Field mapping for structured output
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
│── tests/                    # Unit tests for all modules
├── __init__.py
│   ├── test_email_client.py  
│   ├── test_pdf_parser.py 
│   ├── test_bigquery_client.py  
│── utils/
│   ├── __init__.py
│   ├── config_loader.py  # Loads JSON config files
│   ├── currency_utils.py # Currency conversion functions
│   ├── logging_utils.py  # Custom logging setup


```

## Roadmap
- Add support for multi-currency conversion.
- Implement a web-based dashboard for salary visualization.
- Improve email parsing logic to handle various formats.

## Author
Marko Zagar

