from typing import Optional

from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    DEBUG: bool = True
    
    REDIS_CACHE_URI: Optional[str] = 'redis://redis_cache:6379/0'
    REDIS_CACHE_EXPIRE_SECONDS: Optional[int] = 30 * 60

    OPENWEATHERMAP_API_KEY: Optional[str] = '79bbdef22f7edc6a81180daa87066db5'
    OPENWEATHERMAP_BASE_URL: Optional[str] = 'https://api.openweathermap.org'
    OPENWEATHERMAP_FORECAST_URL: Optional[str] = f'{OPENWEATHERMAP_BASE_URL}/data/2.5/forecast'
    OPENWEATHERMAP_HISTORY_URL: Optional[str] = f'{OPENWEATHERMAP_BASE_URL}/data/2.5/onecall/timemachine'
    OPENWEATHERMAP_GEO_URL: Optional[str] = f'{OPENWEATHERMAP_BASE_URL}/geo/1.0/direct'

    class Config:
        case_sensitive = True
