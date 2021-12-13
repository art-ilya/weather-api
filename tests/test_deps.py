from datetime import datetime, timedelta

import pytest
import pytz
from fastapi import HTTPException
from weather_api.api.dependencies import WeatherQueryParams


def test_query_params_current_date():
    country_code = "RU"
    city = "moScoW"
    local_date = datetime.now(tz=pytz.timezone("Europe/Moscow"))

    params = WeatherQueryParams(
        country_code=country_code,
        city=city,
        date=local_date,
    )

    utc_date = local_date.astimezone(pytz.UTC)
    assert params.date == utc_date
    assert params.country_code == country_code
    assert params.city == city.title()


def test_query_params_past_5_days():
    country_code = "RU"
    city = "Moscow"
    local_date_past = datetime.now(tz=pytz.timezone("Europe/Moscow")) - timedelta(
        days=5, hours=1
    )

    with pytest.raises(HTTPException) as exc:
        _ = WeatherQueryParams(
            country_code=country_code,
            city=city,
            date=local_date_past,
        )

    assert exc.value.status_code == 400


def test_query_params_future_5_days():
    country_code = "RU"
    city = "Moscow"
    local_date_past = datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(
        days=5, hours=1
    )

    with pytest.raises(HTTPException) as exc:
        _ = WeatherQueryParams(
            country_code=country_code,
            city=city,
            date=local_date_past,
        )

    assert exc.value.status_code == 400
