from datetime import datetime, timedelta, timezone

from fastapi import Query, HTTPException
import httpx
from pydantic import validator
from pydantic.dataclasses import dataclass
from settings import config
import aioredis

redis = aioredis.from_url(
    config.REDIS_CACHE_URI,
    encoding="utf-8",
    decode_responses=True,
)


@dataclass
class WeatherQueryParams:
    country_code: str = Query(
        ...,
        min_length=2,
        max_length=2,
        description="Country code (ISO 3166-1 alpha-2 codes)",
        example="RU",
    )
    city: str = Query(
        ...,
        description="City name",
        min_length=1,
        max_length=70,
        example="Moscow",
    )
    date: datetime = Query(
        None,
        description="Datetime ISO-8601 format. If no time zone is specified, then UTC is the default.",
        example="2021-12-12T15:00:00+03:00",
    )

    @validator("city")
    def city_to_title(cls, value: str):
        return value.title()

    @validator("date", pre=True, always=True)
    def convert_to_utc(cls, value: datetime):
        utcnow = datetime.utcnow()
        if value:
            value = value.astimezone(tz=timezone.utc)
            if value.timestamp() < (utcnow - timedelta(days=5)).timestamp():
                raise HTTPException(
                    status_code=400,
                    detail="It is possible to request a weather history no older than 5 days",
                )
            if value.timestamp() > (utcnow + timedelta(days=5)).timestamp():
                raise HTTPException(
                    status_code=400,
                    detail="It is possible to request a weather forecast no further than 5 days",
                )
        else:
            value = utcnow

        return value


async def get_http_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient() as client:
        yield client


async def get_redis_client() -> aioredis.Redis:
    async with redis.client() as client:
        yield client
