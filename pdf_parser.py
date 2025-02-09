import re
import pdfplumber
import logging
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("salary_parser.log"), logging.StreamHandler()]
)


class SalaryParser:
    """
    A parser for extracting salary-related information from a PDF file.

    Args:
        file_name (str): Path to the PDF file.
        config (Dict[str, Any]): Configuration dictionary containing regex patterns.
    """

    def __init__(self, file_name: str, config: Dict[str, Any]):
        """
        Initializes the SalaryParser with the PDF file and configuration.
        """
        self.file_name = file_name
        self.config = config
        self.text = self.extract_text_from_pdf()

    def extract_text_from_pdf(self, start_page: int = 0, end_page: Optional[int] = None) -> Optional[str]:
        """
        Extracts text from all pages (or a specific range) of a PDF file.

        Args:
            start_page (int): First page to extract from (default: 0).
            end_page (Optional[int]): Last page to extract from (default: None for all pages).

        Returns:
            Optional[str]: The extracted text or None if no text is found.
        """
        try:
            with pdfplumber.open(self.file_name) as pdf:
                if end_page is None:
                    end_page = len(pdf.pages)

                text = ""
                for page in pdf.pages[start_page:end_page]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                return text.strip() if text else None
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}", exc_info=True)
            raise

    def extract_salary_date(self) -> Optional[str]:
        """
        Extracts the salary payment date from the text.

        Returns:
            Optional[str]: The extracted salary date, or None if not found.
        """
        match = re.search(self.config.get("salary_date_pattern", ""), self.text)
        return match.group(1) if match else None

    def extract_salary_amounts(self) -> Dict[str, Optional[str]]:
        """
        Extracts salary-related amounts using regex patterns.

        Returns:
            Dict[str, Optional[str]]: A dictionary of extracted salary amounts.
        """
        amounts = {}
        for key, pattern in self.config.get("salary_amounts_patterns", {}).items():
            match = re.search(pattern, self.text)
            amounts[key] = match.group(1).replace(".", "").replace(",", ".") if match else None
        return amounts

    def parse_salary_text(self) -> Dict[str, Any]:
        """
        Parses salary-related information from extracted text.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed data.
        """
        return {
            "salary_date": self.extract_salary_date(),
            "salary_amounts": self.extract_salary_amounts()
        }
