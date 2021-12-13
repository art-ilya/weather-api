from fastapi import FastAPI

from api.v1 import api
from settings import config


def create_app() -> FastAPI:
    app = FastAPI(
        title="weather-api",
        description="Service getting weather data",
        redoc_url=None,
    )

    app.include_router(api.router)

    return app
