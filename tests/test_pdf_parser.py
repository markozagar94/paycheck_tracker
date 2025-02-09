import pytest
from pdf_parser import SalaryParser

TEST_CONFIG = {
    "salary_date_pattern": r"Salary Date:\s*(\d{2}/\d{2}/\d{4})",
    "salary_amounts_patterns": {
        "net_salary": r"Net Salary:\s*([\d,.]+)",
        "gross_salary": r"Gross Salary:\s*([\d,.]+)",
        "tax": r"Tax:\s*([\d,.]+)"
    }
}

MOCK_PDF_TEXT = """
Salary Date: 01/02/2024
Gross Salary: 5.000,00
Tax: 1.000,00
Net Salary: 4.000,00
"""


@pytest.fixture
def mock_salary_parser(mocker):
    """Mock SalaryParser's PDF text extraction method."""
    mocker.patch.object(SalaryParser, "extract_text_from_pdf", return_value=MOCK_PDF_TEXT)
    return SalaryParser("mock_file.pdf", TEST_CONFIG)


def test_extract_salary_date(mock_salary_parser):
    assert mock_salary_parser.extract_salary_date() == "01/02/2024"


def test_extract_salary_amounts(mock_salary_parser):
    amounts = mock_salary_parser.extract_salary_amounts()
    assert amounts["net_salary"] == "4000.00"
    assert amounts["gross_salary"] == "5000.00"
    assert amounts["tax"] == "1000.00"


def test_parse_salary_text(mock_salary_parser):
    parsed_data = mock_salary_parser.parse_salary_text()
    assert parsed_data["salary_date"] == "01/02/2024"
    assert parsed_data["salary_amounts"]["net_salary"] == "4000.00"
    assert parsed_data["salary_amounts"]["gross_salary"] == "5000.00"
    assert parsed_data["salary_amounts"]["tax"] == "1000.00"
