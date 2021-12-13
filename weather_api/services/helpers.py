import json
from datetime import datetime
from typing import Optional

import httpx
from aioredis.client import Redis
from settings import config

from .weather import weather_forecast, weather_history


class WeatherManager:
    def __init__(
        self,
        redis_conn: Redis,
        http_client: httpx.AsyncClient,
        cache_exp_seconds: Optional[int] = None,
        cache_prefix: Optional[str] = "weather",
    ):
        self.redis_conn = redis_conn
        self.http_client = http_client
        if cache_exp_seconds is None:
            self.cache_exp_seconds = config.REDIS_CACHE_EXPIRE_SECONDS
        else:
            self.cache_exp_seconds = cache_exp_seconds
        self.cache_prefix = cache_prefix

    def _get_cache_key(self, country_code: str, city: str, date: datetime) -> str:
        key_ts = int(date.replace(minute=0, second=0, microsecond=0).timestamp())
        return f"{self.cache_prefix}:{country_code.lower()}-{city.lower()}-{key_ts}"

    async def get_weather_data(
        self, country_code: str, city: str, date: datetime
    ) -> dict:
        cache_key = self._get_cache_key(country_code=country_code, city=city, date=date)
        weather_data: str = await self.redis_conn.get(cache_key)
        if weather_data:
            return json.loads(weather_data)

        utc_now = datetime.utcnow()
        if date.timestamp() >= utc_now.timestamp():
            result = await weather_forecast.fetch(
                async_client=self.http_client,
                country_code=country_code,
                city=city,
                date=date,
            )
        else:
            result = await weather_history.fetch(
                async_client=self.http_client,
                country_code=country_code,
                city=city,
                date=date,
            )

        await self.redis_conn.set(
            name=cache_key,
            value=json.dumps(result),
            ex=self.cache_exp_seconds,
        )

        return result
