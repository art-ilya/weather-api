FROM python:3.7

RUN apt-get update
RUN python3 -m pip install --upgrade pip && pip install uvicorn[standard]

WORKDIR /weather_api

COPY ./weather_api/requirements.txt .
RUN pip install -r requirements.txt
COPY ./weather_api .
