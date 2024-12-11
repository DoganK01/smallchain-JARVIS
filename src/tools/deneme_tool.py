from typing import Any

from src.tools.get_weather import WeatherTool
from src.tools.utils import prepare_schemas


other_tools: dict[str, Any] = {
    "get_weather_data": WeatherTool,
}



schemas: str = prepare_schemas(models=[*other_tools.values()])


print(schemas)