import os
import json
import base64
import logging
from typing import Optional

from google.oauth2.credentials import Credentials
from google.cloud import secretmanager
from googleapiclient.discovery import build


class EmailClient:
    def __init__(self, subject_name, label_name,
                 secret_name, output_dir):
        """
        Initializes the EmailClient with customizable parameters for email filtering and attachment handling.

        Args:
            subject_name (str): The subject line to search for in emails.
            label_name (str): The label to filter emails by.
            secret_name (str): The secret name for accessing the Gmail API
        """
        self.subject_name = subject_name
        self.label_name = label_name
        self.secret_name = secret_name
        self.output_dir = output_dir
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

    def fetch_emails(self) -> list[dict]:
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

    def download_attachment(self, message_id) -> Optional[str]:
        """
        Downloads the PDF attachment with the specified file name.

        Args:
            message_id (str): The ID of the email message.
        """

        try:
            logging.info(f"Fetching email!\nMessage id: {message_id}")
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            part = next((p for p in message['payload'].get("parts", []) if p['mimeType'] == 'application/pdf'), None)
            if part:
                attachment_id = part["body"]["attachmentId"]
                file_name = f"{part.get('filename')}"
                output_path = os.path.join(self.output_dir, file_name)

                # Fetch the actual attachment
                attachment = self.service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=attachment_id
                ).execute()

                pdf_data = base64.urlsafe_b64decode(attachment["data"])

                with open(output_path, "wb") as f:
                    f.write(pdf_data)

                logging.info(f"Saved latest salary slip to: {output_path}")
                return output_path
            else:
                logging.warning(f"No PDF attachment found in message {message_id}")
                return None
        except Exception as e:
            logging.error(f"Error downloading attachment {message_id}: {e}")
            return None
