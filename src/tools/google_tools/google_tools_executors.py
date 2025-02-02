import asyncio
import os
from typing import List, Optional, Generator, List
from enum import Enum
from datetime import datetime, timedelta, timezone
from collections import namedtuple
from base64 import urlsafe_b64decode
from loguru import logger

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, EmailStr, ValidationError, ConfigDict, Field

from src.tools.google_tools.google_base import GoogleTool

class EmailLabels(Enum):
    INBOX = "INBOX"
    SENT = "SENT"
    DRAFTS = "DRAFTS"
    SPAM = "SPAM"
    TRASH = "TRASH"


class CalendarColors(Enum):
    BLUE = 1
    GREEN = 2
    PURPLE = 3
    RED = 4
    YELLOW = 5


# --------------- EMAIL OPERATIONS ---------------
class GmailReadTool(GoogleTool):
    """
    Read E-mails from google gmail service
    """
    model_config = ConfigDict(json_schema_extra={"name": "read_gmail_emails"})
    max_results: int = Field(description="Number of emails to read")
    

    async def _arun(self) -> List[str]:
        """
        Fetch, process, and format emails into strings, returning a list of formatted email details.
        """
        label: EmailLabels = EmailLabels.INBOX.value
        service = self.get_service('gmail')
        try:
            email_iterator = iter(self._process_emails(service, label, self.max_results))
            email_strings = []

            while True:
                try:
                    email = next(email_iterator)  # Process the next email
                    formatted_email = self._format_email_details(email)  # Create a string representation
                    email_strings.append(formatted_email)  # Add the string to the list
                except StopIteration:
                    # No more emails to process
                    break

            return email_strings

        except Exception as e:
            logger.info(f"Failed to read emails: {e}")
            return []


    def _get_message_ids(self, service, label: EmailLabels, max_results: int) -> List[str]:
        """
        Fetch message IDs from a specific label.
        """
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=[label], maxResults=max_results)
            .execute()
        )
        return [msg["id"] for msg in results.get("messages", [])]


    def _process_emails(self, service, label: EmailLabels, max_results: int) -> Generator[dict, None, None]:
        """
        Generator to process emails lazily, yielding email details one at a time.
        """
        message_ids = self._get_message_ids(service, label, max_results)
        if not message_ids:
            logger.info("No messages found in label: %s", label)
            return

        for message_id in message_ids:
            try:
                # Fetch the full email details
                msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
                email_details = {
                    "thread_id": msg.get("threadId", "No Thread ID"),
                    "headers": self._extract_headers(msg),
                    "body": self._extract_email_body(msg),
                    "attachments": self._extract_attachments(msg),
                }
                yield email_details
            except Exception as e:
                logger.info("Error processing message %s: %s", message_id, e, exc_info=True)


    def _extract_headers(self, msg: dict) -> dict:
        """
        Extract email headers like 'From', 'To', 'Subject', and 'Date'.
        """
        headers = {header["name"]: header["value"] for header in msg["payload"]["headers"]}
        return {
            "from": headers.get("From", "Unknown"),
            "to": headers.get("To", "Unknown"),
            "subject": headers.get("Subject", "No Subject"),
            "date": headers.get("Date", "Unknown Date"),
        }


    def _extract_email_body(self, msg: dict) -> str:
        """
        Extract the email body, prioritizing plain text over HTML.
        """
        try:
            parts = msg["payload"].get("parts", [])
            for part in parts:
                if part["mimeType"] in ["text/plain", "text/html"]:
                    data = part["body"].get("data")
                    if data:
                        return urlsafe_b64decode(data).decode("utf-8")
            return msg.get("snippet", "No body content available.")
        except Exception as e:
            logger.info("Failed to extract email body: %s", e)
            return "Error extracting email body."


    def _extract_attachments(self, msg: dict) -> List[str]:
        """
        Extract attachment filenames from the email.
        """
        try:
            return [
                part["filename"]
                for part in msg["payload"].get("parts", [])
                if part["filename"]
            ]
        except Exception as e:
            logger.info("Failed to extract attachments: %s", e)
            return []


    def _format_email_details(self, email_details: dict) -> str:
        """
        Format email details into a single string for easy representation.
        """
        headers = email_details["headers"]
        attachments = ", ".join(email_details["attachments"]) if email_details["attachments"] else "None"
        body_snippet = email_details["body"][:2000] + "..." if len(email_details["body"]) > 2000 else email_details["body"]

        return (
            f"--- Email Details ---\n"
            f"Thread ID: {email_details['thread_id']}\n"
            f"Sender: {headers['from']}\n"
            f"Recipient: {headers['to']}\n"
            f"Subject: {headers['subject']}\n"
            f"Date: {headers['date']}\n"
            f"Body (Snippet): {body_snippet}\n"
            f"Attachments: {attachments}\n"
        )

class GmailSendTool(GoogleTool):
    """
    Send e-mails using google gmail service
    """
    model_config = ConfigDict(json_schema_extra={"name": "send_gmail_email"})
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Complete content of the email. Expected to be long text.")

    async def _arun(self) -> List[str]:
        """
        Sends multiple emails based on input requests, returning a list of formatted results.
        Each email request should include 'to', 'subject', 'body', and optionally 'attachments'.
        """
        service = self.get_service('gmail')

        try:
            email_requests: List[dict] = self.as_dict
            email_results = []
            email_iterator = iter(self._process_send_requests(service, email_requests))

            while True:
                try:
                    email_status = next(email_iterator)  # Send the next email
                    formatted_status = self._format_send_status(email_status)  # Format the send status
                    email_results.append(formatted_status)  # Append the formatted status to the list
                except StopIteration:
                    # No more emails to send
                    break

            return email_results

        except Exception as e:
            logger.info("Failed to send emails: %s", e)
            return []


    @property
    def as_dict(self) -> List[dict]:
        """Return the fields of the class as a dictionary."""
        return [self.model_dump(exclude_unset=True)]


    def _process_send_requests(self, service, email_requests: List[dict]) -> Generator[dict, None, None]:
        """
        Generator to process and send email requests lazily, yielding send status for each email.
        """
        for email_request in email_requests:
            try:
                # Extract details from the request
                to_email = email_request["to"]
                subject = email_request["subject"]
                body = email_request["body"]
                attachments = email_request.get("attachments", [])

                # Construct the message
                message = self._create_message(to_email, subject, body, attachments)

                # Send the email
                sent_message = service.users().messages().send(userId="me", body=message).execute()

                # Yield the status of the sent email
                yield {
                    "to": to_email,
                    "subject": subject,
                    "status": "Sent",
                    "message_id": sent_message.get("id", "Unknown ID"),
                }
            except Exception as e:
                # Handle failed email sending
                logger.info("Failed to send email to %s: %s", email_request['to'], e, exc_info=True)
                yield {
                    "to": email_request["to"],
                    "subject": email_request["subject"],
                    "status": f"Failed: {str(e)}",
                }


    def _create_message(self, to_email: str, subject: str, body: str, attachments: List[str]) -> dict:
        """
        Create a MIME message with optional attachments.
        """
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import base64
        import os

        try:
            # Create the email container
            message = MIMEMultipart()
            message["to"] = to_email
            message["subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Add attachments
            for attachment_path in attachments:
                try:
                    part = MIMEBase("application", "octet-stream")
                    with open(attachment_path, "rb") as attachment_file:
                        part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    message.attach(part)
                except Exception as e:
                    logger.info("Failed to attach file %s: %s", attachment_path, e, exc_info=True)

            # Encode the email message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            return {"raw": raw_message}

        except Exception as e:
            logger.info("Error creating message: %s", e)
            return {}


    def _format_send_status(self, email_status: dict) -> str:
        """
        Format the status of a sent email into a single string for easy representation.
        """
        return (
            f"--- Email Send Status ---\n"
            f"To: {email_status['to']}\n"
            f"Subject: {email_status['subject']}\n"
            f"Status: {email_status['status']}\n"
            f"Message ID: {email_status.get('message_id', 'N/A')}\n"
        )


# --------------- CALENDAR OPERATIONS ---------------
class CalendarReadTool(GoogleTool):
    """
    Read events from google calendar service
    """
    model_config = ConfigDict(json_schema_extra={"name": "get_calendar_appointments"})
    max_results: int
    # --- Read Events ---
    async def _arun(self) -> List[str]:
        """
        Lazily reads calendar events and returns a list of formatted results.
        """
        service = self.get_service('calendar')
        logger.add("calendar_events.log", level="INFO", rotation="10 MB")

        try:
            days_ahead: int = 365
            now = datetime.now(tz=timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()
            logger.info(f"Fetching events from {time_min} to {time_max}")

            event_results = []
            event_iterator = self._get_event_iterator(service, self.max_results, time_min, time_max)

            while True:
                try:
                    event_details = next(event_iterator)  # Fetch next event details lazily
                    formatted_event = self._format_event_details(event_details)
                    event_results.append(formatted_event)
                    logger.info(f"Event details fetched successfully: {event_details['summary']}")
                except StopIteration:
                    logger.info("All events processed successfully.")
                    break  # Stop when all events are fetched

            return event_results

        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")
            return []

    def _get_event_iterator(self, service, max_results: int, time_min: str, time_max: str) -> Generator[dict, None, None]:
        """
        Generator to fetch calendar events lazily, yielding the event details one by one.
        """
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            logger.warning("No events found.")
        
        for event in events:
            try:
                # Yield event details lazily
                yield {
                    "summary": event.get("summary", "No Title"),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "description": event.get("description", "No Description"),
                    "location": event.get("location", "No Location"),
                    "attendees": [attendee["email"] for attendee in event.get("attendees", [])],
                    "event_id": event.get("id", "N/A"),
                    "html_link": event.get("htmlLink", "N/A"),
                }
            except KeyError as e:
                logger.error(f"Error extracting data from event: {e}")
                yield {"summary": "Unknown Event", "status": f"Failed: {e}"}

    def _format_event_details(self, event_details: dict) -> str:
        """
        Format the event details into a readable string.
        """
        logger.debug(f"Formatting event details for: {event_details['summary']}")
        return (
            f"--- Calendar Event Details ---\n"
            f"Summary: {event_details['summary']}\n"
            f"Start: {event_details['start']}\n"
            f"End: {event_details['end']}\n"
            f"Description: {event_details['description']}\n"
            f"Location: {event_details['location']}\n"
            f"Attendees: {', '.join(event_details['attendees'])}\n"
            f"Event ID: {event_details['event_id']}\n"
            f"HTML Link: {event_details['html_link']}\n"
        )

class CalendarInsertTool(GoogleTool):
    """
    Insert events using google calendar service
    """
    model_config = ConfigDict(json_schema_extra={"name": "insert_calendar_appointment"})
    summary: str = Field(description="Appointment summary")
    location: str = Field(description="Appointment location", examples=["123 Main Street, Conference Room A, San Francisco, CA", "Online"])
    description: str = Field(description="Appointment description")
    start_time: str = Field(description="Start time in RFC3339 format", examples=["2024-12-20T09:00:00Z"])
    end_time: str = Field(description="End time in RFC3339 format", examples=["2024-11-10T20:30:00Z"])
    attendees: Optional[list[str]] = Field(default=None, description="List of attendee email addresses", examples=["john.doe@gmail.com", "jane.smith@gmail.com"])

    # --- Create Events ---
    async def _arun(self) -> List[str]:
        """
        Lazily creates calendar events and returns a list of formatted results.
        """
        service = self.get_service('calendar')
        logger.add("calendar_events.log", level="INFO", rotation="10 MB")  # Log file setup
        try:
            event_requests = self.as_dict
            event_results = []
            event_iterator = self._process_event_requests(service, event_requests)

            while True:
                try:
                    event_status = next(event_iterator)  # Create the next event lazily
                    formatted_status = self._format_event_status(event_status)
                    event_results.append(formatted_status)
                    logger.info(f"Event created successfully: {event_status['summary']}")
                except StopIteration:
                    logger.info("All events processed successfully.")
                    break  # Stop when all events are created

            return event_results

        except Exception as e:
            logger.error(f"Failed to process events: {e}")
            return []
        
    @property
    def as_dict(self) -> List[dict]:
        """Return the fields of the class as a dictionary."""
        return [self.model_dump(exclude_unset=True)]

    def _process_event_requests(self, service, event_requests: List[dict]) -> Generator[dict, None, None]:
        """
        Generator to process and create calendar events lazily, yielding the event status for each.
        """
        for event_request in event_requests:
            try:
                # Prepare the event body
                event_body = self._build_event_body(event_request)

                # Create the event using the Calendar API
                created_event = (
                    service.events()
                    .insert(calendarId="primary", body=event_body)
                    .execute()
                )

                logger.info(f"Successfully created event: {event_request['summary']}")
                # Yield success status
                yield {
                    "summary": event_request["summary"],
                    "status": "Created",
                    "event_id": created_event.get("id", "Unknown ID"),
                    "html_link": created_event.get("htmlLink", "N/A"),
                    "location": event_request.get("location", "No location provided"),
                }

            except Exception as e:
                # Handle failure to create the event
                logger.error(f"Failed to create event '{event_request['summary']}': {e}")
                yield {
                    "summary": event_request["summary"],
                    "status": f"Failed: {str(e)}",
                    "event_id": None,
                    "html_link": None,
                    "location": None,
                }

    def _build_event_body(self, event_request: dict) -> dict:
        """
        Build the request body for creating a calendar event.
        """
        color: CalendarColors = CalendarColors.BLUE

        logger.debug(f"Building event body for: {event_request['summary']}")
        event_body = {
            "summary": event_request["summary"],
            "description": event_request.get("description", ""),
            "start": {
                "dateTime": event_request["start_time"],
                "timeZone": event_request.get("time_zone", "UTC"),
            },
            "end": {
                "dateTime": event_request["end_time"],
                "timeZone": event_request.get("time_zone", "UTC"),
            },
            "attendees": [{"email": email} for email in event_request.get("attendees", [])],
            "colorId": color.value,
            "reminders": {
                "useDefault": False,
                "overrides": event_request.get(
                    "reminders", [{"method": "email", "minutes": 24 * 60}]
                ),
            },
        }
    
        if "location" in event_request and event_request["location"]:
            event_body["location"] = event_request["location"]
            logger.debug(f"Added location: {event_request['location']}")

        return event_body

    def _format_event_status(self, event_status: dict) -> str:
        """
        Format the event creation status into a readable string.
        """
        logger.debug(f"Formatting event status for: {event_status['summary']}")
        return (
            f"--- Calendar Event Status ---\n"
            f"Summary: {event_status['summary']}\n"
            f"Status: {event_status['status']}\n"
            f"Event ID: {event_status.get('event_id', 'N/A')}\n"
            f"HTML Link: {event_status.get('html_link', 'N/A')}\n"
            f"Location: {event_status.get('location', 'No location provided')}\n"
        )

# --------------- MAIN FUNCTIONALITY ---------------
from src.tools.google_tools.credentials import GoogleCredsManager

async def main():

    google_creds_manager = GoogleCredsManager()
    # Setup logging
    logger.add("app.log", level="INFO", rotation="10 MB")
    
    # Gmail - Read Emails
    try:
        # Create an instance of GmailReadTool with some configurations
        gmail_read_tool = GmailReadTool(
            google_creds_manager=google_creds_manager,
            max_results=5, label="INBOX")
        
        # Fetch the emails asynchronously
        email_strings = await gmail_read_tool._arun()

        if email_strings:
            logger.info("Fetched Emails:")
            logger.info(email_strings)
        else:
            logger.warning("No emails found.")
    except Exception as e:
        logger.error(f"Error while fetching emails: {e}")

    # Gmail - Send Emails (example)
    try:
        # Create an instance of GmailSendTool with example data
        gmail_send_tool = GmailSendTool(
            google_creds_manager=google_creds_manager,
            to="e200504010@stud.tau.edu.tr", 
            subject="Test Subject", 
            body="This is a test email body."
        )
        
        # Send the email asynchronously
        email_results = await gmail_send_tool._arun()

        if email_results:
            logger.info("Emails Sent:")
            logger.info(email_results)
        else:
            logger.warning("Failed to send emails.")
    except Exception as e:
        logger.error(f"Error while sending emails: {e}")
    
    # Google Calendar - Read Events
    try:
        # Create an instance of CalendarReadTool
        calendar_read_tool = CalendarReadTool(google_creds_manager=google_creds_manager, max_results=5)
        
        # Fetch the calendar events asynchronously
        event_strings = await calendar_read_tool._arun()

        if event_strings:
            logger.info("Fetched Calendar Events:")

            logger.info(event_strings)
        else:
            logger.warning("No calendar events found.")
    except Exception as e:
        logger.error(f"Error while fetching calendar events: {e}")
    
    # Google Calendar - Create Event
    try:
        # Create an instance of CalendarInsertTool with example event data
        calendar_insert_tool = CalendarInsertTool(
            google_creds_manager=google_creds_manager,
            summary="Team Meeting",
            location="Online",
            description="Discuss project updates",
            start_time="2024-12-25T09:00:10Z",
            end_time="2024-12-25T10:00:15Z",
            attendees=["attendee1@example.com", "attendee2@example.com"]
        )
        
        # Create the event asynchronously
        insert_result = await calendar_insert_tool._arun()

        if insert_result:
            logger.info("Event Created Successfully:")

            logger.info(insert_result)
        else:
            logger.warning("Failed to create event.")
    except Exception as e:
        logger.error(f"Error while creating calendar event: {e}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
