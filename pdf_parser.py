import re
import pdfplumber
import logging
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validates the configuration dictionary.

    Args:
        config (Dict[str, Any]): The configuration dictionary.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    required_keys = {"salary_date_pattern", "salary_amounts_patterns"}
    if not required_keys.issubset(config.keys()):
        logging.error("Configuration is missing required keys.", extra={"missing_keys": required_keys - config.keys()})
        return False
    return True


class SalaryParser:
    """
    A parser for extracting salary-related information from a PDF file.

    Args:
        file_name (str): Path to the PDF file.
        config (Dict[str, Any]): Configuration dictionary containing regex patterns.

    Raises:
        ValueError: If the configuration is invalid or missing required keys.
    """

    def __init__(self, file_name: str, config: Dict[str, Any]):
        """
        Initializes the SalaryParser with the PDF file and configuration.
        """
        self.file_name = file_name
        if not validate_config(config):
            raise ValueError("Invalid or missing configuration.")
        self.config = config
        self.text = self.extract_text_from_pdf()
        if self.text is None:
            logger.error(f"No text extracted from PDF: {self.file_name}")

    def extract_text_from_pdf(self, start_page: int = 0, end_page: Optional[int] = None) -> Optional[str]:
        """
        Extracts text from all pages (or a specific range) of a PDF file.

        Args:
            start_page (int): First page to extract from (default: 0).
            end_page (Optional[int]): Last page to extract from (default: None for all pages).

        Returns:
            Optional[str]: The extracted text or None if no text is found.
        """
        logging.info(f"Extracting text from PDF: {self.file_name}")
        try:
            with pdfplumber.open(self.file_name) as pdf:
                if end_page is None:
                    end_page = len(pdf.pages)

                text = ""
                for i, page in enumerate(pdf.pages[start_page:end_page]):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    logging.debug(f"Extracted text from page {start_page + i + 1}")

                if text:
                    logging.info("Text extraction completed successfully.")
                    return text.strip()
                else:
                    logging.warning("No text found in PDF.")
                    return None
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
        if match:
            return match.group(1)
        logging.warning("Salary date not found in text.")
        return None

    def extract_salary_amounts(self) -> Dict[str, Optional[str]]:
        """
        Extracts salary-related amounts using regex patterns.

        Returns:
            Dict[str, Optional[str]]: A dictionary of extracted salary amounts.
        """
        amounts = {}
        for key, pattern in self.config.get("salary_amounts_patterns", {}).items():
            match = re.search(pattern, self.text)
            if match:
                amounts[key] = match.group(1).replace(".", "").replace(",", ".")  # Convert to float format
            else:
                logging.warning(f"No match found for pattern: {pattern}")
                amounts[key] = None
        return amounts

    def parse_salary_text(self) -> Dict[str, Any]:
        """
        Parses salary-related information from extracted text.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed data.
        """
        return {
            "salary_date": self.extract_salary_date(),
            **self.extract_salary_amounts()
        }