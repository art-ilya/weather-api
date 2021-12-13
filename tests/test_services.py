from datetime import datetime, timedelta
import json

import aioredis
import pytest
from weather_api.services.helpers import WeatherManager


@pytest.mark.asyncio
async def test_weather_manager_current_date(async_redis_client: aioredis.Redis, async_http_client):
    country_code = "RU"
    city = "Saint Petersburg"
    date = datetime.utcnow()
    cache_prefix = "test_weather"
    manager = WeatherManager(
        redis_conn=async_redis_client,
        http_client=async_http_client,
        cache_exp_seconds=60,
        cache_prefix=cache_prefix,
    )
    cache_key = manager._get_cache_key(
        country_code=country_code,
        city=city,
        date=date,
    )

    keys_count = await async_redis_client.exists(cache_key)
    assert keys_count == 0

    result = await manager.get_weather_data(
        country_code=country_code,
        city=city,
        date=date,
    )
    
    keys_count = await async_redis_client.exists(cache_key)
    cached_json = await async_redis_client.get(cache_key)
    await async_redis_client.delete(cache_key)
    
    assert len(result) > 0
    assert keys_count == 1
    assert json.loads(cached_json) == result
