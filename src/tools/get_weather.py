import aiohttp
from pydantic import ConfigDict, Field

from src.tools.base import AsyncBaseTool
from src.settings import settings


class WeatherTool(AsyncBaseTool):
    """
    Fetch detailed weather data using OpenWeatherMap API asynchronously
    """
    model_config = ConfigDict(json_schema_extra={"name": "get_weather_data"})
    location: str = Field(description="Location to get weather data for", examples="New York")

    async def _arun(self):
        """
        Asynchronous method to fetch weather data from OpenWeatherMap.
        """
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.location,  # Location: city name or "lat,lon"
            "appid": settings.WEATHER_API_KEY,  # OpenWeatherMap API key
            "units": "metric",  # Metric units (Celsius, m/s)
            "lang": "en"  # Language for weather description
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(base_url, params=params) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    weather_data = await response.json()  # Parse the JSON response

                    # Extract and return weather details
                    details = {
                        "location": f"{weather_data['name']}, {weather_data['sys']['country']}",
                        "coordinates": weather_data["coord"],
                        "weather_main": weather_data["weather"][0]["main"],
                        "weather_description": weather_data["weather"][0]["description"],
                        "temperature": {
                            "current": weather_data["main"]["temp"],
                            "feels_like": weather_data["main"]["feels_like"],
                            "min": weather_data["main"]["temp_min"],
                            "max": weather_data["main"]["temp_max"]
                        },
                        "humidity": weather_data["main"]["humidity"],
                        "pressure": weather_data["main"]["pressure"],
                        "wind": {
                            "speed": weather_data["wind"]["speed"],
                            "direction_deg": weather_data["wind"].get("deg", None),
                            "gust": weather_data["wind"].get("gust", None)
                        },
                        "clouds": weather_data["clouds"].get("all", 0),
                        "sunrise": weather_data["sys"]["sunrise"],
                        "sunset": weather_data["sys"]["sunset"],
                        "timezone_offset": weather_data["timezone"]
                    }
                    print(details)

                    result = (
                        f"Weather in {details['location']}:\n"
                        f"- Condition: {details['weather_main']} ({details['weather_description']})\n"
                        f"- Temperature: {details['temperature']['current']}°C "
                        f"(Feels like: {details['temperature']['feels_like']}°C)\n"
                        f"  Min: {details['temperature']['min']}°C, Max: {details['temperature']['max']}°C\n"
                        f"- Humidity: {details['humidity']}%\n"
                        f"- Pressure: {details['pressure']} hPa\n"
                        f"- Wind: {details['wind']['speed']} m/s, "
                        f"Direction: {details['wind']['direction_deg'] or 'N/A'}°\n"
                        f"- Cloudiness: {details['clouds']}%\n"
                    )
                    return result

            except aiohttp.ClientResponseError as e:
                # Handle HTTP-related errors, e.g., 404, 500
                error_message = f"HTTP Error {e.status}: {e.message}"
                print(error_message)
                raise RuntimeError(f"Failed to fetch weather data: {error_message}") from e

            except aiohttp.ClientError as e:
                # Handle other aiohttp-related errors
                print(f"Client error occurred: {e}")
                raise RuntimeError("A network error occurred while fetching weather data.") from e

            except Exception as e:
                # Handle any other unforeseen errors
                print(f"An unexpected error occurred: {e}")
                raise RuntimeError("An unexpected error occurred.") from e

