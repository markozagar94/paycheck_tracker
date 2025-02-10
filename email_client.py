import os
import re
import json
import base64
import logging
from typing import Optional, List

from google.oauth2.credentials import Credentials
from google.cloud import secretmanager
from googleapiclient.discovery import build


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("email_client.log"), logging.StreamHandler()]
)


class EmailClient:
    """
    A client for fetching emails and downloading attachments from Gmail using the Gmail API.

    Attributes:
        subject_name (str): The subject line to search for in emails.
        label_name (str): The label to filter emails by.
        secret_name (str): The name of the secret in GCP Secret Manager containing Gmail API credentials.
        output_dir (str): The directory to save downloaded attachments.
        creds (Credentials): Authorized credentials for accessing the Gmail API.
        service (Resource): The Gmail API service instance.
    """

    def __init__(self, subject_name: str, label_name: str, secret_name: str, output_dir: str):
        """
        Initializes the EmailClient with customizable parameters for email filtering and attachment handling.

        Args:
            subject_name (str): The subject line to search for in emails.
            label_name (str): The label to filter emails by.
            secret_name (str): The secret name for accessing the Gmail API.
            output_dir (str): The directory to save downloaded attachments.
        """
        self.subject_name = subject_name
        self.label_name = label_name
        self.secret_name = secret_name
        self.output_dir = output_dir

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.creds = self._get_gmail_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _get_gmail_credentials(self) -> Credentials:
        """
        Fetches Gmail API credentials from GCP Secret Manager.

        Returns:
            Credentials: Authorized credentials for accessing the Gmail API.
        """
        # Initialize the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        logging.info(f"Fetching secret from GCP Secret Manager!\nSecret name: {self.secret_name}")

        try:
            # Access the secret
            response = client.access_secret_version(request={"name": self.secret_name})
            credentials_json = response.payload.data.decode("UTF-8")

            # Parse the JSON credentials
            credentials_info = json.loads(credentials_json)
            return Credentials.from_authorized_user_info(credentials_info)

        except Exception as e:
            logging.error(f"Failed to fetch Gmail credentials: {e}")
            raise

    def fetch_emails(self) -> List[dict]:
        """
        Fetches emails with the specified label and subject.

        Returns:
            list: A list of email messages matching the criteria.
        """
        query = f'label:{self.label_name} subject:"{self.subject_name}"'
        logging.info(f"Fetching emails! Search query: {query}")
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            return results.get('messages', [])
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
            return []

    def download_attachment(self, message_id: str) -> Optional[List[str]]:
        """
        Downloads all PDF attachments from the specified email message.

        Args:
            message_id (str): The ID of the email message.

        Returns:
            list: Paths to the downloaded PDF files.
        """
        try:
            logging.info(f"Fetching email!\nMessage id: {message_id}")
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            output_paths = []

            for part in message['payload'].get("parts", []):
                if part['mimeType'] == 'application/pdf':
                    attachment_id = part["body"]["attachmentId"]
                    file_name = f"{part.get('filename')}"
                    creation_date = None
                    for header in part["headers"]:
                        if header["name"] == "Content-Disposition":
                            match = re.search(r'creation-date="([^"]+)"', header["value"])
                            if match:
                                creation_date = match.group(1).replace(",", "").replace(":", "").replace(" ", "_")
                    filename, ext = file_name.rsplit(".", 1)
                    new_filename = f"{filename}_{creation_date}.{ext}"

                    output_path = os.path.join(self.output_dir, new_filename, )

                    # Fetch the actual attachment
                    attachment = self.service.users().messages().attachments().get(
                        userId="me", messageId=message_id, id=attachment_id
                    ).execute()

                    pdf_data = base64.urlsafe_b64decode(attachment["data"])

                    with open(output_path, "wb") as f:
                        f.write(pdf_data)

                    logging.info(f"Saved PDF attachment to: {output_path}")
                    output_paths.append(output_path)

            if not output_paths:
                logging.warning(f"No PDF attachments found in message {message_id}")

            return output_paths
        except Exception as e:
            logging.error(f"Error downloading attachments for message {message_id}: {e}")
            return []
