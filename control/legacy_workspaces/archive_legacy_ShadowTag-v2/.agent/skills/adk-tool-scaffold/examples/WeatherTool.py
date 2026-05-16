from google.adk.tools import BaseTool


class WeatherTool(BaseTool):
  """
  Get current weather for a city.
  """

  def execute(self, city: str) -> dict:
    """
    Fetches weather data.
    """
    # Mock implementation for example purposes
    return {"city": city, "temp": 72, "condition": "Sunny"}

  def get_schema(self) -> dict:
    return {
      "type": "object",
      "properties": {
        "city": {"type": "string", "description": "The city to get weather for"}
      },
      "required": ["city"],
    }
