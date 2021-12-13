from dataclasses import asdict

import aioredis
import httpx
from fastapi import APIRouter, Depends
from schemas.common import responses
from schemas.weather import WeatherResponse
from services.helpers import WeatherManager

from api.dependencies import WeatherQueryParams, get_http_client, get_redis_client

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
)


@router.get(
    "/",
    response_model=WeatherResponse,
    responses={
        400: responses[400],
        503: responses[503]
    },
)
async def get_weather(
    params: WeatherQueryParams = Depends(WeatherQueryParams),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    redis_client: aioredis.Redis = Depends(get_redis_client),
):
    weather_manager = WeatherManager(redis_conn=redis_client, http_client=http_client)
    result = await weather_manager.get_weather_data(**asdict(params))
    return result
