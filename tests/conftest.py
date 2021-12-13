import asyncio
import logging
import os
import sys
from pathlib import Path
import httpx
import aioredis

import pytest

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir.joinpath('weather_api')))

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
default_logger = logging.getLogger(__name__)


REDIS_DSN = "redis://redis_cache:6379/1"
redis = aioredis.from_url(
    REDIS_DSN,
    encoding="utf-8",
    decode_responses=True,
)


@pytest.fixture
async def async_redis_client():
    async with redis.client() as client:
        yield client


@pytest.fixture
async def async_http_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient() as client:
        yield client
