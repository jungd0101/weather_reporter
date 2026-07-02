# Automated Weather Reporter

A lightweight command-line tool that fetches and displays current weather conditions for any city in the world.

## How It Works
1. **Geocoding** — the city name you provide is resolved to latitude/longitude coordinates using the [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api).
2. **Forecast fetch** — those coordinates are used to request current conditions (temperature, humidity, precipitation, wind speed, and weather description) from the [Open-Meteo Forecast API](https://open-meteo.com/).
3. **Error handling** — network timeouts, connection failures, malformed responses, and unmatched city names are all caught and reported with a clear message instead of a raw stack trace.

No API key or account signup is required — Open-Meteo's free tier is open access.

## Requirements
```bash
pip install requests
```

## Usage
```bash
python weather_reporter.py Seoul
python weather_reporter.py "New York" --units imperial
```

### Options
| Flag | Default | Description |
|---|---|---|
| `-u, --units` | `metric` | `metric` for °C / km/h, `imperial` for °F / mph |

### Example Output

Weather for Seoul, South Korea
Conditions:   Mainly clear
Temperature:  24.3 degC
Feels like:   25.1 degC
Humidity:     55%
Precipitation: 0.0 mm
Wind speed:   12.4 km/h

## Notes
- City names that match multiple places (e.g. "Springfield") will resolve to the first/most prominent match returned by the geocoding API.
- All API calls have an 8-second timeout to avoid hanging indefinitely on a bad connection.
