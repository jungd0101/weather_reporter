import argparse
import sys
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 8

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def geocode_city(city_name):
    try:
        response = requests.get(
            GEOCODE_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("The location lookup timed out. Check your connection and try again.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to the geocoding service. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Location lookup failed with an HTTP error: {e}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Received an invalid response from the geocoding service.")

    results = data.get("results")
    if not results:
        raise RuntimeError(f"No location found matching '{city_name}'. Try being more specific.")

    top = results[0]
    return {
        "name": top.get("name", city_name),
        "country": top.get("country", ""),
        "admin1": top.get("admin1", ""),
        "latitude": top["latitude"],
        "longitude": top["longitude"],
    }


def fetch_weather(latitude, longitude, units):
    temperature_unit = "fahrenheit" if units == "imperial" else "celsius"
    wind_speed_unit = "mph" if units == "imperial" else "kmh"

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                           "precipitation,weather_code,wind_speed_10m",
                "temperature_unit": temperature_unit,
                "wind_speed_unit": wind_speed_unit,
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("The weather request timed out. Check your connection and try again.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to the weather service. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Weather request failed with an HTTP error: {e}")

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Received an invalid response from the weather service.")

    current = data.get("current")
    if current is None:
        raise RuntimeError("The weather service response was missing current conditions.")

    return current


def format_report(location, current, units):
    temp_symbol = "F" if units == "imperial" else "C"
    wind_symbol = "mph" if units == "imperial" else "km/h"

    description = WEATHER_CODES.get(current.get("weather_code"), "Unknown conditions")
    place = location["name"]
    if location["admin1"]:
        place += f", {location['admin1']}"
    if location["country"]:
        place += f", {location['country']}"

    lines = [
        f"Weather for {place}",
        "-" * (len(place) + 12),
        f"Conditions:   {description}",
        f"Temperature:  {current.get('temperature_2m')} deg{temp_symbol}",
        f"Feels like:   {current.get('apparent_temperature')} deg{temp_symbol}",
        f"Humidity:     {current.get('relative_humidity_2m')}%",
        f"Precipitation: {current.get('precipitation')} mm",
        f"Wind speed:   {current.get('wind_speed_10m')} {wind_symbol}",
    ]
    return "\n".join(lines)


def get_report(city_name, units):
    location = geocode_city(city_name)
    current = fetch_weather(location["latitude"], location["longitude"], units)
    return format_report(location, current, units)


def main():
    parser = argparse.ArgumentParser(description="Get the current weather for any city from the command line.")
    parser.add_argument("city", nargs="+", help="City name, e.g. 'Seoul' or 'New York'")
    parser.add_argument(
        "-u", "--units", choices=["metric", "imperial"], default="metric",
        help="Units to display temperature and wind speed in (default: metric)"
    )
    args = parser.parse_args()
    city_name = " ".join(args.city)

    try:
        print(get_report(city_name, args.units))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
