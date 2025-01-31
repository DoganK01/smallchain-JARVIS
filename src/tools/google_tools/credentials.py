import os
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pydantic import BaseModel, Field

from src.settings import settings


class GoogleCredsConfig(BaseModel):
    """Configuration for Google credentials."""

    client_secrets_file_path: Optional[Path] = Field(default=Path(settings.GOOGLE_CREDENTIALS_PATH))
    token_file_path: Optional[Path] = Field(default=Path("token.json"))


class GoogleCredsManager(GoogleCredsConfig):
    """Google Credential Manager."""

    def get_credentials(self, scopes: List[str]) -> Credentials:

        creds: Optional[Credentials] = None

        if os.path.exists(self.token_file_path):
            creds = Credentials.from_authorized_user_file(filename=self.token_file_path, scopes=scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file_path, scopes)
                creds = flow.run_local_server(port=0)

                with open(file=self.token_file_path, mode="w") as token:
                    token.write(creds.to_json())

        return creds
