import unittest
from unittest.mock import patch
from pdf_parser import SalaryParser


class TestSalaryParser(unittest.TestCase):
    """Test suite for SalaryParser."""

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

    def setUp(self):
        """Set up a mock SalaryParser instance."""
        with patch.object(SalaryParser, "extract_text_from_pdf", return_value=self.MOCK_PDF_TEXT):
            self.parser = SalaryParser("mock_file.pdf", self.TEST_CONFIG)

    def test_extract_salary_date(self):
        """Test extracting the salary date."""
        self.assertEqual(self.parser.extract_salary_date(), "01/02/2024")

    def test_extract_salary_amounts(self):
        """Test extracting salary amounts."""
        amounts = self.parser.extract_salary_amounts()
        self.assertEqual(amounts["net_salary"], "4000.00")
        self.assertEqual(amounts["gross_salary"], "5000.00")
        self.assertEqual(amounts["tax"], "1000.00")

    def test_parse_salary_text(self):
        """Test parsing salary text into structured data."""
        parsed_data = self.parser.parse_salary_text()
        self.assertEqual(parsed_data["salary_date"], "01/02/2024")
        self.assertEqual(parsed_data["net_salary"], "4000.00")
        self.assertEqual(parsed_data["gross_salary"], "5000.00")
        self.assertEqual(parsed_data["tax"], "1000.00")


if __name__ == '__main__':
    unittest.main()
