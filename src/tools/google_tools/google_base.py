from typing import Optional
from abc import abstractmethod

from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError

from src.tools.base import AsyncBaseTool
from src.tools.google_tools.services import GoogleServices
from src.tools.google_tools.credentials import GoogleCredsManager


class GoogleTool(AsyncBaseTool):

    google_creds_manager: Optional[GoogleCredsManager] = None

    async def arun(self):
        return await self._arun()

    @abstractmethod
    async def _arun(self):
        pass
    
    def get_service(self, service_name: str):
        """
        Build and return a Google service client based on the service name.
        
        Args:
            service_name (str): Name of the Google service (e.g., 'gmail', 'calendar').

        Returns:
            googleapiclient.discovery.Resource: The Google service client.

        Raises:
            ValueError: If the service name is not supported.
        """
        # Retrieve all Google services from the Enum
        available_services = {service.value.name.lower(): service.value for service in GoogleServices}
        
        # Check if the requested service is available
        if service_name.lower() not in available_services:
            raise ValueError(f"Service '{service_name}' is not supported. Supported services: {list(available_services.keys())}")
        
        # Get the service configuration
        service = available_services[service_name.lower()]
        scopes = GoogleServices.get_all_scopes()
        credentials = self.google_creds_manager.get_credentials(scopes=scopes)
        version = "v1" if service.name.lower() == "gmail" else "v3"
        # Build and return the Google API client
        #return build(service.name.lower(), version, credentials=credentials)
        try:
            # Attempt to build the service client
            api_client = build(service.name.lower(), version, credentials=credentials)
            print(f"Successfully created {service.name.lower()} client.")
            return api_client
        except GoogleAuthError as auth_error:
            print(f"Authentication failed: {auth_error}")
            raise  # Re-raise the exception after logging it
        except Exception as e:
            print(f"Error creating service client for {service_name}: {e}")
            raise  # Re-raise the exception after logging it