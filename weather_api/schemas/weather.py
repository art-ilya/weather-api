from typing import List
from pydantic import BaseModel


class WeatherDescription(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class WeatherResponse(BaseModel):
    dt: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    clouds: int
    wind_speed: float
    wind_deg: float
    wind_gust: float
    visibility: int
    weather: List[WeatherDescription]




