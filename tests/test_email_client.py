import os
import unittest
import tempfile
from email_client import EmailClient


class TestEmailClient(unittest.TestCase):
    def setUp(self):
        """Set up test environment and initialize EmailClient."""
        self.temp_dir = tempfile.mkdtemp()  # Use a temporary directory for storing PDFs
        self.client = EmailClient(
            subject_name="FW: Isplatna lista",
            label_name="Isplatna lista",
            pdf_file_name="Isplatna lista Zagar Marko.pdf",
            secret_name="projects/882776592425/secrets/gmail-api-credentials/versions/latest",
            output_dir=self.temp_dir
        )

    def test_fetch_emails(self):
        """Test fetching emails with the specified label and subject."""
        emails = self.client.fetch_emails()
        self.assertIsInstance(emails, list)

    def test_download_attachment(self):
        """Test downloading an attachment from the first available email."""
        emails = self.client.fetch_emails()
        if not emails:
            self.skipTest("No emails found for testing attachment download.")

        pdf_file_path = self.client.download_attachment(emails[0]['id'])

        self.assertIsNotNone(pdf_file_path, "Failed to download PDF")
        self.assertTrue(os.path.exists(pdf_file_path), f"File not found: {pdf_file_path}")

    def tearDown(self):
        """Clean up temporary directory after tests."""
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)


if __name__ == '__main__':
    unittest.main()
