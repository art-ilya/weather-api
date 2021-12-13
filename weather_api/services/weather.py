from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import List, Optional, Tuple

from fastapi.exceptions import HTTPException
from settings import config
from httpx import AsyncClient, HTTPError


class WeatherService(ABC):
    @abstractmethod
    async def fetch(
        self, async_client: AsyncClient, country_code: str, city: str, date: datetime
    ) -> dict:
        """Retrieves data from some weather service"""


class OpenWeatherForecastService(WeatherService):
    def __init__(
        self,
        api_url: str,
        api_key: str,
        units: str = "metric",
        logger: logging.Logger = None,
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.units = units
        self.logger = logger or logging.getLogger(__name__)

    def _get_query_params(self, country_code: str, city: str) -> dict:
        return {
            "q": f"{city},{country_code}",
            "appid": self.api_key,
            "units": self.units,
        }

    def _get_closest_data(self, weather_data: dict, date: datetime) -> Optional[dict]:
        """
        weather_data = {
            ...
            "list": [
                {
                    "dt": 1639332000,
                    "main": {...},
                    "weather": [...],
                    "clouds": {...},
                    "wind": {...},
                    "visibility": 10000,
                    "pop": 0,
                    "sys": {...},
                    "dt_txt": "2021-12-12 18:00:00"
                },
                ...
            ]
            ...
        }
        """

        def _get_flatten_data(data: dict) -> dict:
            """Helper function for formatting the response"""
            result = {k: v for k, v in data.items() if not isinstance(v, dict)}
            result.update(**data["main"])
            result.update({"clouds": data["clouds"]["all"]})
            result.update({f"wind_{k}": v for k, v in data["wind"].items()})
            return result

        data_list: List[dict] = weather_data.get("list", [])
        target_dt = date.timestamp()
        result = min(data_list, key=lambda x: abs(x["dt"] - target_dt), default=None)
        return _get_flatten_data(result)

    async def fetch(
        self, async_client: AsyncClient, country_code: str, city: str, date: datetime
    ) -> dict:
        try:
            params = self._get_query_params(country_code=country_code, city=city)
            response = await async_client.get(self.api_url, params=params)
            self.logger.info(f'Fetched openweather data')
            response.raise_for_status()
            return self._get_closest_data(weather_data=response.json(), date=date)
        except HTTPError as exc:
            self.logger.error(f"Error while requesting {exc.request.url!r}: {exc}")
            raise HTTPException(status_code=503, detail=str(exc))


class OpenWeatherHistoryService(WeatherService):
    def __init__(
        self,
        api_url: str,
        api_geo_url: str,
        api_key: str,
        units: str = "metric",
        logger: logging.Logger = None,
    ) -> None:
        self.api_url = api_url
        self.api_geo_url = api_geo_url
        self.api_key = api_key
        self.units = units
        self.logger = logger or logging.getLogger(__name__)

    def _get_weather_query_params(self, lat: float, lon: float, date: datetime) -> dict:
        return {
            "lat": lat,
            "lon": lon,
            "dt": int(date.timestamp()),
            "appid": self.api_key,
            "units": self.units,
        }

    def _get_geo_query_params(self, country_code: str, city: str) -> dict:
        return {
            "q": f"{city},{country_code}",
            "limit": 1,
            "appid": self.api_key,
        }

    def _get_closest_data(self, weather_data: dict, date: datetime) -> Optional[dict]:
        """
        weather_data = {
            ...
            "hourly": [
                {
                    "dt": 1639267200,
                    "temp": -10.89,
                    "feels_like": -16.99,
                    "pressure": 1034,
                    "humidity": 89,
                    "dew_point": -12.19,
                    "uvi": 0,
                    "clouds": 100,
                    "visibility": 10000,
                    "wind_speed": 3.35,
                    "wind_deg": 126,
                    "wind_gust": 11.07,
                    "weather": [...]
                },
                ...
            ]
            ...
        }
        """
        data_list = weather_data.get("hourly", [])
        target_dt = date.timestamp()
        result = min(data_list, key=lambda x: abs(x["dt"] - target_dt), default=None)
        return result

    async def _get_lat_lon(
        self, async_client: AsyncClient, country_code: str, city: str
    ) -> Tuple[float, float]:
        params = self._get_geo_query_params(country_code=country_code, city=city)
        response = await async_client.get(self.api_geo_url, params=params)
        response.raise_for_status()
        data_list = response.json()
        if not data_list:
            raise HTTPException(status_code=400, detail="Invalid city/country_code")
        return (data_list[0]["lat"], data_list[0]["lon"])

    async def fetch(
        self, async_client: AsyncClient, country_code: str, city: str, date: datetime
    ) -> dict:
        try:
            lat, lon = await self._get_lat_lon(
                async_client=async_client, country_code=country_code, city=city
            )
            self.logger.info(f'Fetched lat, lon: {lat}, {lon}')
            params = self._get_weather_query_params(lat=lat, lon=lon, date=date)
            response = await async_client.get(self.api_url, params=params)
            self.logger.info(f'Fetched openweather data')
            response.raise_for_status()
            return self._get_closest_data(weather_data=response.json(), date=date)
        except HTTPError as exc:
            self.logger.error(f"Error while requesting {exc.request.url!r}: {exc}")
            raise HTTPException(status_code=503, detail=str(exc))


weather_forecast = OpenWeatherForecastService(
    api_url=config.OPENWEATHERMAP_FORECAST_URL,
    api_key=config.OPENWEATHERMAP_API_KEY,
)

weather_history = OpenWeatherHistoryService(
    api_url=config.OPENWEATHERMAP_HISTORY_URL,
    api_geo_url=config.OPENWEATHERMAP_GEO_URL,
    api_key=config.OPENWEATHERMAP_API_KEY,
)

