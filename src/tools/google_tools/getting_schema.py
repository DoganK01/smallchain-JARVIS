from typing import Any

from src.tools.google_tools.google_maps_tool import GoogleMapsTool
from src.tools.get_weather import WeatherTool
from src.tools.utils import prepare_schemas
from src.tools.google_tools.google_tools_executors import GmailReadTool, GmailSendTool, CalendarReadTool, CalendarInsertTool

other_tools: dict[str, Any] = {
    "google_maps": GoogleMapsTool,
    "get_weather_data": WeatherTool,
    "read_gmail_emails": GmailReadTool,
    "send_gmail_email": GmailSendTool,
    "get_calendar_appointments": CalendarReadTool,
    "insert_calendar_appointment": CalendarInsertTool
}



schemas: str = prepare_schemas(models=[*other_tools.values()])


print(schemas)